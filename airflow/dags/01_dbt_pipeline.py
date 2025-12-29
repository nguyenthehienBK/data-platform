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



DAG_NAME = '01_dbt_pipeline'
SCHEDULE_INTERVAL = '30 07 * * *'
DBT_PROJECT_PATH = "/opt/dbt/data_pipeline"
DBT_PROFILE_PATH = os.path.join(DBT_PROJECT_PATH, "profiles.yml")

args = {
    'owner': 'airflow',
    'start_date': pendulum.today(tz=Timezone('Asia/Ho_Chi_Minh')).add(days=-1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
    'catchup': False,
}

basic_cosmos_dag = DbtDag(
    # dbt/cosmos-specific parameters
    project_config=ProjectConfig(
            dbt_project_path=DBT_PROJECT_PATH,
    ),
    profile_config=ProfileConfig(
            profile_name="data_pipeline",
            profiles_yml_filepath=DBT_PROFILE_PATH,
            target_name="dev"
    ),
    render_config=RenderConfig(
            select=["tag:mart", "tag:staging"],
            exclude=["tag:daily"],
    ),
    # normal dag parameters
    schedule=SCHEDULE_INTERVAL,
    start_date=pendulum.today(tz=Timezone('Asia/Ho_Chi_Minh')).add(days=-1),
    catchup=False,
    dag_id=DAG_NAME,
    default_args={"retries": 2},
)
