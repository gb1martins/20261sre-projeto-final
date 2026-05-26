from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Adiciona o diretório /opt/airflow/app ao path para importar o etl.py
sys.path.append('/opt/airflow/app')

from etl import process_bronze, process_silver, process_gold, get_s3_client, get_clickhouse_client

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 5, 26),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_bronze():
    s3 = get_s3_client()
    process_bronze(s3)

def run_silver():
    s3 = get_s3_client()
    ch = get_clickhouse_client()
    process_silver(s3, ch)

def run_gold():
    ch = get_clickhouse_client()
    process_gold(ch)

with DAG(
    'northwind_medallion_pipeline',
    default_args=default_args,
    description='Pipeline Medallion para o projeto Northwind (Bronze -> Silver -> Gold)',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['northwind', 'etl'],
) as dag:

    task_bronze = PythonOperator(
        task_id='ingest_to_bronze',
        python_callable=run_bronze,
    )

    task_silver = PythonOperator(
        task_id='transform_to_silver',
        python_callable=run_silver,
    )

    task_gold = PythonOperator(
        task_id='aggregate_to_gold',
        python_callable=run_gold,
    )

    task_bronze >> task_silver >> task_gold
