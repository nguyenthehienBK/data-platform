import os
import pendulum
from pendulum.tz.timezone import Timezone
from datetime import timedelta

from cosmos import (
    DbtDag,
    ProjectConfig,
    ProfileConfig,
    RenderConfig,
)


DBT_PROJECT_PATH = "/opt/dbt/data_pipeline"
DBT_PROFILE_PATH = os.path.join(DBT_PROJECT_PATH, "profiles.yml")

default_args = {
    'owner': 'airflow',
    'start_date': pendulum.today(tz=Timezone('Asia/Ho_Chi_Minh')).add(days=-1),
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
    'catchup': False,
}

gold_dag = DbtDag(
    project_config=ProjectConfig(
        dbt_project_path=DBT_PROJECT_PATH,
    ),
    profile_config=ProfileConfig(
        profile_name="data_pipeline",
        profiles_yml_filepath=DBT_PROFILE_PATH,
        target_name="dev",
    ),
    render_config=RenderConfig(
        select=["tag:gold"],
    ),
    schedule="30 7 * * *",
    catchup=False,
    dag_id="dbt_crbt_silver_to_gold",
    default_args=default_args,
)
