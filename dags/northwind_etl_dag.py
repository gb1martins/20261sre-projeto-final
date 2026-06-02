from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Adiciona o diretório /opt/airflow/app ao path para importar o etl.py
sys.path.append('/opt/airflow/app')

from etl import (
    process_bronze_file, 
    process_silver_orders, 
    process_silver_order_details, 
    process_gold, 
    get_s3_client, 
    get_clickhouse_client, 
    check_connections
)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 26),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_bronze_orders():
    s3 = get_s3_client()
    process_bronze_file(s3, 'northwind_orders.csv')

def run_bronze_details():
    s3 = get_s3_client()
    process_bronze_file(s3, 'northwind_order_details.csv')

def run_silver_orders():
    s3 = get_s3_client()
    ch = get_clickhouse_client()
    process_silver_orders(s3, ch)

def run_silver_details():
    s3 = get_s3_client()
    ch = get_clickhouse_client()
    process_silver_order_details(s3, ch)

def run_gold():
    ch = get_clickhouse_client()
    process_gold(ch)

def run_pre_flight():
    check_connections()

with DAG(
    'northwind_medallion_pipeline',
    default_args=default_args,
    description='Pipeline Medallion para o projeto Northwind (Bronze -> Silver -> Gold)',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['northwind', 'etl'],
) as dag:

    task_pre_flight = PythonOperator(
        task_id='pre_flight_check',
        python_callable=run_pre_flight,
    )

    # Camada Bronze em Paralelo
    task_bronze_orders = PythonOperator(
        task_id='ingest_orders_to_bronze',
        python_callable=run_bronze_orders,
    )

    task_bronze_details = PythonOperator(
        task_id='ingest_details_to_bronze',
        python_callable=run_bronze_details,
    )

    # Camada Silver em Paralelo
    task_silver_orders = PythonOperator(
        task_id='transform_orders_to_silver',
        python_callable=run_silver_orders,
    )

    task_silver_details = PythonOperator(
        task_id='transform_details_to_silver',
        python_callable=run_silver_details,
    )

    task_gold = PythonOperator(
        task_id='aggregate_to_gold',
        python_callable=run_gold,
    )

    # Fluxo com Paralelismo: 
    # Orders e Details são independentes até a Camada Gold.
    task_pre_flight >> [task_bronze_orders, task_bronze_details]
    
    task_bronze_orders >> task_silver_orders
    task_bronze_details >> task_silver_details
    
    [task_silver_orders, task_silver_details] >> task_gold

