import os
import logging

from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")
AIRFLOW_HOME = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")

# dataset_file = "yellow_tripdata_2021-01.csv"
# dataset_url = f"https://s3.amazonaws.com/nyc-tlc/trip+data/{dataset_file}"
# parquet_file = dataset_file.replace('.csv', '.parquet')
# BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')

def format_to_parquet(src_file, dest_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(src_file)
    pq.write_table(table, dest_file)


# NOTE: takes 20 mins, at an upload speed of 800kbps. Faster if your internet has a better upload speed
def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    # storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    # storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


default_args = {
    "owner": "airflow",
    "start_date": days_ago(1),
    "depends_on_past": False,
    "retries": 1,
}

# For zones we will be reusing these steps so let's define a function
def download_parquetize_upload_dag(
    dag
    , url_template
    , local_csv_path_template
    , local_parquet_path_template
    , gcs_path_template
):

    with dag:
        download_dataset_task = BashOperator(
            task_id="download_dataset_task",
            bash_command=f"curl -sSLf {url_template} > {local_csv_path_template}"
        )

        format_to_parquet_task = PythonOperator(
            task_id="format_to_parquet_task",
            python_callable=format_to_parquet,
            op_kwargs={
                "src_file": local_csv_path_template,
                "dest_file": local_parquet_path_template
            },
        )

        # TODO: Homework - research and try XCOM to communicate output values between 2 tasks/operators
        local_to_gcs_task = PythonOperator(
            task_id="local_to_gcs_task",
            python_callable=upload_to_gcs,
            op_kwargs={
                "bucket": BUCKET,
                "object_name": gcs_path_template,
                "local_file": local_parquet_path_template,
            },
        )

        remove_dataset_task = BashOperator(
            task_id="remove_dataset_task",
            bash_command=f"rm {local_csv_path_template} {local_parquet_path_template}"
        )    

        download_dataset_task >> format_to_parquet_task >> local_to_gcs_task >> remove_dataset_task


# In order to iterate through the data files, we start by setting the base URL
URL_PREFIX = 'https://s3.amazonaws.com/nyc-tlc/trip+data'

# We could repeat with green taxi data and follow the predefined format
GREEN_TAXI_URL_TEMPLATE = URL_PREFIX + '/green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
GREEN_TAXI_CSV_FILE_TEMPLATE = AIRFLOW_HOME + '/green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
GREEN_TAXI_PARQUET_FILE_TEMPLATE = AIRFLOW_HOME + '/green_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.parquet'
GREEN_TAXI_GCS_PATH_TEMPLATE = "raw/green_tripdata/{{ execution_date.strftime(\'%Y\') }}/{{ execution_date.strftime(\'%Y-%m\') }}.parquet"

green_taxi_data_dag = DAG(
    dag_id="green_taxi_data_ingestion_gcs_dag",
    schedule_interval="0 7 2 * *",
    start_date=datetime(2019, 1, 1),
    default_args=default_args,
    catchup=True,
    max_active_runs=3,
    tags=['dtc-de'],
)

download_parquetize_upload_dag(
    dag=green_taxi_data_dag
    , url_template=GREEN_TAXI_URL_TEMPLATE
    , local_csv_path_template=GREEN_TAXI_CSV_FILE_TEMPLATE
    , local_parquet_path_template=GREEN_TAXI_PARQUET_FILE_TEMPLATE
    , gcs_path_template=GREEN_TAXI_GCS_PATH_TEMPLATE
)
