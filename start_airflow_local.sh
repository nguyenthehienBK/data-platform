# Remove exists airflow service
docker compose -f docker-compose-local.yaml down
while true
do
    if docker ps  | grep airflow; then
        echo "Waiting for down airflow service completed, sleep 3 second"
        sleep 3
    else
        break
    fi
done

echo "Up airflow service"
docker compose -f docker-compose-local.yaml up -d