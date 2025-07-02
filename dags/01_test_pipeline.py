import pendulum
from pendulum.tz.timezone import Timezone
from datetime import timedelta

from airflow.models import DAG
from airflow.operators.empty import EmptyOperator


DAG_NAME = '01_test_pipeline'
SCHEDULE_INTERVAL = '30 07 * * *'

args = {
    'owner': 'airflow',
    'start_date': pendulum.today(tz=Timezone('Asia/Ho_Chi_Minh')).add(days=-1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'catchup': False,
}

with DAG(
    dag_id=DAG_NAME,
    default_args=args,
    schedule=SCHEDULE_INTERVAL,
    tags=["test"]
) as dag:
    start_pipeline = EmptyOperator(task_id="start_pipeline")
    final_task = EmptyOperator(task_id="final_pipeline")

    start_pipeline >> final_task