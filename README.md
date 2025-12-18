# data-pipeline
## Deploy Airflow Local
- Create `.env` file and edit with your configs
    ```console
    cd data-pipeline
    cp .env.example .env
    vim .env
    ```
- Up Airflow 
    ```console
    sh start_airflow_local.sh
    ``` 
- Down Airflow
    ```console
    docker compose -f docker-compose-local.yaml down
    ```

## Build extend Airflow image
*You should build your own extended Airflow image to install additional requirements.*

- Add your packages to the `requirements.txt` file, then execute the following command:
    ```console
    cd data-pipeline
    sh build-extend-images.sh [version]
    ```