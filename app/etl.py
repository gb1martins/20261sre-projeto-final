import os
import boto3
import clickhouse_connect
import pandas as pd
import numpy as np
from io import BytesIO
from otel_setup import setup_otel, flush_otel
import time

# OTel Setup
meter, tracer = setup_otel("northwind-etl")

# Business Metrics
revenue_counter = meter.create_counter(
    "business.revenue.total",
    unit="USD",
    description="Total Net Revenue processed"
)
orders_counter = meter.create_counter(
    "business.orders.count",
    unit="1",
    description="Total orders processed"
)
process_duration = meter.create_histogram(
    "etl.process.duration",
    unit="ms",
    description="Duration of ETL process per layer"
)

# Configurações
S3_ENDPOINT = os.getenv("S3_ENDPOINT_URL", "http://localhost:9000")
S3_KEY = os.getenv("AWS_ACCESS_KEY_ID", "minioadmin")
S3_SECRET = os.getenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "northwind")

CH_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CH_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
CH_USER = os.getenv("CLICKHOUSE_USER", "northwind")
CH_PASS = os.getenv("CLICKHOUSE_PASSWORD", "northwind")

# Batch Processing: Tamanho do chunk para processamento de arquivos CSV
CHUNK_SIZE = 10000

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

def check_connections():
    """Valida a conectividade com MinIO e ClickHouse (Pre-flight Check)."""
    print("--- Pre-flight Check: Verificando Infraestrutura ---")
    
    # Validar S3 (MinIO)
    try:
        s3 = get_s3_client()
        s3.list_buckets()
        print("✅ Conexão com MinIO: OK")
    except Exception as e:
        print(f"❌ Erro de conexão com MinIO: {e}")
        raise

    # Validar ClickHouse
    try:
        ch = get_clickhouse_client()
        ch.command("SELECT 1")
        print("✅ Conexão com ClickHouse: OK")
    except Exception as e:
        print(f"❌ Erro de conexão com ClickHouse: {e}")
        raise

def process_bronze_file(s3_client, file_name):
    """Lê um arquivo local e salva como RAW no MinIO (Camada Bronze)."""
    with tracer.start_as_current_span("process_bronze_file") as span:
        span.set_attribute("file_name", file_name)
        # Garantir que o bucket existe
        try:
            s3_client.create_bucket(Bucket=S3_BUCKET)
        except (s3_client.exceptions.BucketAlreadyOwnedByYou, s3_client.exceptions.BucketAlreadyExists):
            pass

        local_path = f'/data/{file_name}'
        if os.path.exists(local_path):
            s3_key = f'bronze/{file_name}'
            print(f"Subindo {local_path} para s3://{S3_BUCKET}/{s3_key}...")
            s3_client.upload_file(local_path, S3_BUCKET, s3_key)
            span.set_attribute("status", "success")
        else:
            print(f"Aviso: Arquivo {local_path} não encontrado.")
            span.set_attribute("status", "not_found")
    
    flush_otel()

def process_bronze(s3_client):
    """Lê arquivos locais e salva como RAW no MinIO (Camada Bronze)."""
    with tracer.start_as_current_span("process_bronze") as span:
        start_time = time.time()
        print("--- Camada Bronze: Iniciando Ingestão Raw ---")
        files = ['northwind_orders.csv', 'northwind_order_details.csv']
        for file_name in files:
            process_bronze_file(s3_client, file_name)
        
        duration = (time.time() - start_time) * 1000
        process_duration.record(duration, {"layer": "bronze"})
        span.set_attribute("etl.layer", "bronze")
        span.set_attribute("etl.duration_ms", duration)
    
    flush_otel()

def process_silver_orders(s3_client, ch_client):
    """Lê Orders da Bronze, limpa, tipa e salva no ClickHouse (Camada Prata) em chunks."""
    with tracer.start_as_current_span("process_silver_orders") as span:
        print(f"Processando silver_orders em chunks de {CHUNK_SIZE} (Batch Processing)...")
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key='bronze/northwind_orders.csv')
        
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
        
        total_orders = 0
        # Ler o stream do S3 em chunks
        for chunk in pd.read_csv(obj['Body'], chunksize=CHUNK_SIZE):
            chunk['order_date'] = pd.to_datetime(chunk['order_date']).dt.date
            chunk['shipped_date'] = pd.to_datetime(chunk['shipped_date']).dt.date
            chunk['required_date'] = pd.to_datetime(chunk['required_date']).dt.date
            chunk['freight'] = chunk['freight'].fillna(0).astype(float)
            chunk = chunk.replace({np.nan: None})
            
            ch_client.insert('silver_orders', chunk[cols_orders].values.tolist(), column_names=cols_orders)
            total_orders += len(chunk)
        
        orders_counter.add(total_orders)
        span.set_attribute("business.orders_count", total_orders)
    
    flush_otel()

def process_silver_order_details(s3_client, ch_client):
    """Lê Order Details da Bronze, limpa, tipa e salva no ClickHouse (Camada Prata) em chunks."""
    with tracer.start_as_current_span("process_silver_order_details") as span:
        print(f"Processando silver_order_details em chunks de {CHUNK_SIZE} (Batch Processing)...")
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key='bronze/northwind_order_details.csv')
        
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
        
        total_revenue = 0
        # Ler o stream do S3 em chunks
        for chunk in pd.read_csv(obj['Body'], chunksize=CHUNK_SIZE):
            chunk['unit_price'] = chunk['unit_price'].astype(float)
            chunk['quantity'] = chunk['quantity'].astype(int)
            chunk['discount'] = chunk['discount'].astype(float)
            
            # Calcular receita para métricas
            chunk_revenue = (chunk['unit_price'] * chunk['quantity'] * (1 - chunk['discount'])).sum()
            total_revenue += chunk_revenue
            
            ch_client.insert('silver_order_details', chunk[cols_details].values.tolist(), column_names=cols_details)
        
        revenue_counter.add(total_revenue)
        span.set_attribute("business.revenue", total_revenue)
    
    flush_otel()

def process_silver(s3_client, ch_client):
    """Lê da Bronze, limpa, tipa e salva no ClickHouse (Camada Prata)."""
    with tracer.start_as_current_span("process_silver") as span:
        start_time = time.time()
        print("--- Camada Prata: Limpeza e Estruturação ---")
        process_silver_orders(s3_client, ch_client)
        process_silver_order_details(s3_client, ch_client)
        
        duration = (time.time() - start_time) * 1000
        process_duration.record(duration, {"layer": "silver"})
        span.set_attribute("etl.layer", "silver")
        span.set_attribute("etl.duration_ms", duration)
    
    flush_otel()

def process_gold(ch_client):
    """Cria visões/tabelas agregadas para negócio (Camada Ouro)."""
    with tracer.start_as_current_span("process_gold") as span:
        start_time = time.time()
        print("--- Camada Ouro: Agregações Analíticas ---")
        
        # 1. Métricas por Pedido
        ch_client.command("DROP TABLE IF EXISTS gold_order_metrics")
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

        # 2. Ranking de Produtos por Receita Líquida
        ch_client.command("DROP TABLE IF EXISTS gold_product_ranking")
        ch_client.command("""
        CREATE TABLE gold_product_ranking ENGINE = MergeTree() ORDER BY product_id AS
        SELECT 
            product_id,
            round(SUM(unit_price * quantity * (1 - discount)), 2) AS net_revenue,
            SUM(quantity) AS total_quantity
        FROM silver_order_details
        GROUP BY product_id
        """)

        # 3. Série Temporal Mensal de Receita Líquida
        ch_client.command("DROP TABLE IF EXISTS gold_monthly_revenue")
        ch_client.command("""
        CREATE TABLE gold_monthly_revenue ENGINE = MergeTree() ORDER BY month AS
        SELECT 
            toStartOfMonth(o.order_date) AS month,
            round(SUM(d.unit_price * d.quantity * (1 - d.discount)), 2) AS net_revenue,
            COUNT(DISTINCT o.order_id) AS total_orders
        FROM silver_orders o
        JOIN silver_order_details d ON o.order_id = d.order_id
        GROUP BY month
        """)
        
        duration = (time.time() - start_time) * 1000
        process_duration.record(duration, {"layer": "gold"})
        span.set_attribute("etl.layer", "gold")
        span.set_attribute("etl.duration_ms", duration)
        print("Tabelas da Camada Ouro criadas com sucesso.")
    
    flush_otel()

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
