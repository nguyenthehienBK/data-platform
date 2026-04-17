import os
import pendulum
from pendulum.tz.timezone import Timezone
from datetime import timedelta

from airflow import DAG
from cosmos import (
    DbtTaskGroup,
    ProjectConfig,
    ProfileConfig,
    RenderConfig,
)
from airflow.providers.standard.operators.bash import BashOperator


DBT_PROJECT_PATH = "/opt/dbt/data_pipeline"
DBT_PROFILE_PATH = os.path.join(DBT_PROJECT_PATH, "profiles.yml")

project_config = ProjectConfig(
    dbt_project_path=DBT_PROJECT_PATH,
)
profile_config = ProfileConfig(
    profile_name="data_pipeline",
    profiles_yml_filepath=DBT_PROFILE_PATH,
    target_name="dev",
)

default_args = {
    'owner': 'airflow',
    'start_date': pendulum.today(tz=Timezone('Asia/Ho_Chi_Minh')).add(days=-1),
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    dag_id="dbt_crbt_bronze_to_silver",
    schedule="0 * * * *",
    catchup=False,
    default_args=default_args,
) as dag:

    check_source_freshness = BashOperator(
        task_id="check_source_freshness",
        bash_command="dbt source freshness --project-dir {{ params.project_dir }} --profiles-dir {{ params.project_dir }}",
        params={"project_dir": DBT_PROJECT_PATH},
    )

    silver = DbtTaskGroup(
        group_id="silver",
        project_config=project_config,
        profile_config=profile_config,
        render_config=RenderConfig(
            select=["tag:silver"],
        ),
    )

    check_source_freshness >> silver
