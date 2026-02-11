# Data Platform

This repository contains an on-premise data platform.
Each component has its own README inside its folder, use it for more detail.

## Quickstart

- Lakehouse

```
cd lakehouse
sh run_spark_hudi.sh
```
- Mock data

Run all cells in http://localhost:8888/lab/tree/06-mock-data.ipynb

- OpenMetadata
```
cd governance/open-metadata
sh run_openmetadata.sh
```

- MCP trino
```
cd agent/mcp-trino
docker compose up --build -d
```

- Ranger

https://github.com/apache/ranger

## Service – Port Mapping

<!-- PORT_TABLE_START -->
| Category | Service | Host | Port | Protocol | Notes |
|--------|--------|------|------|----------|----------|
|Orchestration| airflow-apiserver | localhost | 8000 | TCP/HTTP |||
|Orchestration| airflow-worker | - | 8080 | TCP/HTTP |||
|Orchestration| airflow-scheduler | - | 8080 | TCP/HTTP |||
|Orchestration| airflow-trigger | - | 8080 | TCP/HTTP |||
|Orchestration| airflow-dag-processor | - | 8080 | TCP/HTTP |||
|Orchestration| airflow-postgres | - | 5432 | TCP/HTTP |||
|Orchestration| airflow-redis | - | 6379 | TCP/HTTP |||
|Query Engine| spark ui | localhost | 4040 | TCP/HTTP |||
|Query Engine| spark master | localhost | 7077 | TCP/HTTP |||
|Query Engine| spark master ui | localhost | 8080 | TCP/HTTP |||
|Query Engine| spark worker ui | localhost | 8081 | TCP/HTTP |||
|Query Engine| spark history ui | localhost | 18080 | TCP/HTTP |||
|Query Engine| spark thrift | localhost | 10000 | TCP/HTTP |||
|Query Engine| trino | localhost | 28080 | TCP/HTTP |||
|Storage| minio api | localhost | 9000 | TCP/HTTP |||
|Storage| minio ui | localhost | 9001 | TCP/HTTP | admin/password||
|Metadata| hive-metastore | localhost | 9083 | TCP/HTTP |||
|Consumption| jupyter | localhost | 8888 | TCP/HTTP |||
|Consumption| superset | - | - | - |||
|Governance| ranger | localhost | 6080 | TCP/HTTP |admin/rangerR0cks!|
|Governance| openmetadata | localhost | 8585 | TCP/HTTP |admin@open-metadata.org/admin||
|Governance| mysql | localhost | 3306 | TCP/HTTP |||
|Governance| elasticsearch | localhost | 9200;9300 | TCP/HTTP |||
|Governance| ingestion | localhost | 38080 | TCP/HTTP |||
|Governance| dbt | - | - | - |||
<!-- PORT_TABLE_END -->
