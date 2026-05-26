import os
import boto3
import clickhouse_connect
import pandas as pd
import numpy as np
from io import BytesIO

# Configurações
S3_ENDPOINT = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
S3_KEY = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
S3_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "northwind")

CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
CH_USER = os.getenv("CLICKHOUSE_USER", "northwind")
CH_PASS = os.getenv("CLICKHOUSE_PASSWORD", "northwind")

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_KEY,
        aws_secret_access_key=S3_SECRET,
        region_name='us-east-1'
    )

def get_clickhouse_client():
    return clickhouse_connect.get_client(host=CH_HOST, port=CH_PORT, username=CH_USER, password=CH_PASS)

def process_bronze(s3_client):
    """Lê arquivos locais e salva como RAW no MinIO (Camada Bronze)."""
    print("--- Camada Bronze: Iniciando Ingestão Raw ---")
    files = ['northwind_orders.csv', 'northwind_order_details.csv']
    
    # Garantir que o bucket existe
    try:
        s3_client.create_bucket(Bucket=S3_BUCKET)
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        pass
    except s3_client.exceptions.BucketAlreadyExists:
        pass

    for file_name in files:
        local_path = f'/data/{file_name}'
        if os.path.exists(local_path):
            s3_key = f'bronze/{file_name}'
            print(f"Subindo {local_path} para s3://{S3_BUCKET}/{s3_key}...")
            s3_client.upload_file(local_path, S3_BUCKET, s3_key)
        else:
            print(f"Aviso: Arquivo {local_path} não encontrado.")

def process_silver(s3_client, ch_client):
    """Lê da Bronze, limpa, tipa e salva no ClickHouse (Camada Prata)."""
    print("--- Camada Prata: Limpeza e Estruturação ---")
    
    # 1. Processar Orders
    print("Processando silver_orders...")
    obj = s3_client.get_object(Bucket=S3_BUCKET, Key='bronze/northwind_orders.csv')
    df_orders = pd.read_csv(BytesIO(obj['Body'].read()))
    
    # Limpeza e Tipagem
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date']).dt.date
    df_orders['shipped_date'] = pd.to_datetime(df_orders['shipped_date']).dt.date
    df_orders['required_date'] = pd.to_datetime(df_orders['required_date']).dt.date
    df_orders['freight'] = df_orders['freight'].fillna(0).astype(float)
    
    # Clickhouse connect e Nullable(Date) precisam de None para NaT
    df_orders = df_orders.replace({np.nan: None})
    
    ch_client.command("DROP TABLE IF EXISTS silver_orders")
    ch_client.command("""
    CREATE TABLE silver_orders (
        order_id UInt32,
        customer_id String,
        employee_id UInt32,
        order_date Date,
        required_date Date,
        shipped_date Nullable(Date),
        ship_via UInt32,
        freight Float64,
        ship_name String,
        ship_city String,
        ship_country String
    ) ENGINE = MergeTree() ORDER BY order_id
    """)
    
    cols_orders = ['order_id', 'customer_id', 'employee_id', 'order_date', 'required_date', 'shipped_date', 'ship_via', 'freight', 'ship_name', 'ship_city', 'ship_country']
    ch_client.insert('silver_orders', df_orders[cols_orders].values.tolist(), column_names=cols_orders)

    # 2. Processar Order Details
    print("Processando silver_order_details...")
    obj = s3_client.get_object(Bucket=S3_BUCKET, Key='bronze/northwind_order_details.csv')
    df_details = pd.read_csv(BytesIO(obj['Body'].read()))
    
    df_details['unit_price'] = df_details['unit_price'].astype(float)
    df_details['quantity'] = df_details['quantity'].astype(int)
    df_details['discount'] = df_details['discount'].astype(float)
    
    ch_client.command("DROP TABLE IF EXISTS silver_order_details")
    ch_client.command("""
    CREATE TABLE silver_order_details (
        order_id UInt32,
        product_id UInt32,
        unit_price Float64,
        quantity UInt32,
        discount Float64
    ) ENGINE = MergeTree() ORDER BY (order_id, product_id)
    """)
    
    cols_details = ['order_id', 'product_id', 'unit_price', 'quantity', 'discount']
    ch_client.insert('silver_order_details', df_details[cols_details].values.tolist(), column_names=cols_details)

def process_gold(ch_client):
    """Cria visões/tabelas agregadas para negócio (Camada Ouro)."""
    print("--- Camada Ouro: Agregações Analíticas ---")
    
    ch_client.command("DROP TABLE IF EXISTS gold_order_metrics")
    
    # Criando uma tabela ouro com métricas consolidadas
    ch_client.command("""
    CREATE TABLE gold_order_metrics ENGINE = MergeTree() ORDER BY order_id AS
    SELECT 
        o.order_id,
        o.customer_id,
        o.order_date,
        o.ship_country,
        SUM(d.unit_price * d.quantity * (1 - d.discount)) AS total_order_value,
        SUM(d.quantity) AS total_items,
        o.freight
    FROM silver_orders o
    JOIN silver_order_details d ON o.order_id = d.order_id
    GROUP BY o.order_id, o.customer_id, o.order_date, o.ship_country, o.freight
    """)
    print("Tabela gold_order_metrics criada com sucesso.")

def main():
    print("Iniciando Pipeline Medallion (Bronze -> Silver -> Gold)...")
    try:
        s3 = get_s3_client()
        ch = get_clickhouse_client()
        
        process_bronze(s3)
        process_silver(s3, ch)
        process_gold(ch)
        
        print("Pipeline finalizado com sucesso!")
    except Exception as e:
        print(f"Erro no pipeline: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
