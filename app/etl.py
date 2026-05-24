import os
import boto3
import clickhouse_connect
import pandas as pd
from io import BytesIO

# Configurações
S3_ENDPOINT = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
S3_KEY = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
S3_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "northwind")

CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET,
        region_name='us-east-1'
    )

def upload_initial_data(s3_client):
    """Sobe o arquivo CSV local para o MinIO se ele existir."""
    local_path = 'data/northwind_orders.csv'
    if os.path.exists(local_path):
        print(f"Subindo {local_path} para o bucket {S3_BUCKET}...")
        try:
            # Garantir que o bucket existe
            try:
                s3_client.create_bucket(Bucket=S3_BUCKET)
            except s3_client.exceptions.BucketAlreadyOwnedByYou:
                pass
            
            s3_client.upload_file(local_path, S3_BUCKET, 'raw/northwind_orders.csv')
            print("Upload concluído.")
        except Exception as e:
            print(f"Erro no upload para S3: {e}")

def main():
    print("Iniciando processo ETL...")
    
    s3 = get_s3_client()
    upload_initial_data(s3)
    
    # 1. Conectar ao ClickHouse e preparar tabela
    try:
        client = clickhouse_connect.get_client(host=CH_HOST, port=CH_PORT)
        
        client.command("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id UInt32,
            customer_id String,
            order_date Date,
            total_amount Float64
        ) ENGINE = MergeTree()
        ORDER BY order_id
        """)
        print("Tabela 'orders' pronta.")

        # 2. Ler dados do MinIO
        print(f"Lendo dados de s3://{S3_BUCKET}/raw/northwind_orders.csv...")
        obj = s3.get_object(Bucket=S3_BUCKET, Key='raw/northwind_orders.csv')
        df = pd.read_csv(BytesIO(obj['Body'].read()))
        
        # 3. Carga Idempotente (Simples: Limpa antes de carregar)
        # Em produção, usaríamos uma lógica de controle de duplicados mais refinada
        client.command("TRUNCATE TABLE orders")
        
        # 4. Inserir no ClickHouse
        client.insert('orders', df.values.tolist(), column_names=list(df.columns))
        print(f"Sucesso! {len(df)} registros carregados no ClickHouse.")

    except Exception as e:
        print(f"Erro durante o processo ETL: {e}")

if __name__ == "__main__":
    main()
