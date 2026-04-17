# Data Platform

On-premise data platform built with open-source components.

## Architecture

```
┌─────────────────┐     ┌─────────────────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Source DB      │────▶│   Streaming                  │────▶│   Lakehouse     │────▶│   Consumption   │
│   (PostgreSQL)   │     │   Debezium → Kafka (Avro)    │     │   Spark/Hudi    │     │   dbt + Airflow │
└─────────────────┘     └─────────────────────────────┘     └─────────────────┘     └─────────────────┘
                                                                     │
                                                                    Trino
                                                                     │
                                                              ┌─────────────────┐     ┌─────────────────┐
                                                              │   Agent          │     │   Governance    │
                                                              │   MCP Trino      │     │   OpenMetadata  │
                                                              └─────────────────┘     └─────────────────┘
```

**Data Flow:**
1. **Debezium** captures CDC events from PostgreSQL (CRBT tables + orders)
2. **Kafka** + **Apicurio Registry** streams Avro-serialized events
3. **Spark Structured Streaming** reads from Kafka, writes to **Hudi COW** tables in **MinIO** (bronze layer)
4. **dbt** (via Airflow/Cosmos) transforms bronze → silver → gold through Hudi tables
5. **Trino** provides SQL query access across all layers

## Quickstart

### 1. Lakehouse (Spark + Hudi + MinIO + Trino)

```bash
cd lakehouse
./build.sh                # First time only
./run_spark_hudi.sh start
```

Then run notebooks at http://localhost:8888:
- `01-mock-data.ipynb` — load static reference data into Hudi tables
- `02-streaming.ipynb` — start CDC streaming from Kafka to bronze layer

### 2. Streaming (Kafka + Debezium)

```bash
cd stream
docker compose up -d
```

Register the Debezium source connector:
```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @connectors/source-connector-postgres.json
```

### 3. Airflow + dbt

```bash
cd airflow
cp .env.example .env      # Edit with your config
sh start_airflow_local.sh
```

DAGs:
- `dbt_crbt_bronze_to_silver` — hourly, transforms bronze → silver
- `dbt_crbt_silver_to_gold` — daily, transforms silver → gold

### 4. Governance (OpenMetadata)

```bash
cd governance/open-metadata
sh run_openmetadata.sh start
```

### 5. MCP Trino Agent

```bash
cd agent/mcp-trino
docker compose up --build -d
```

## Service Ports

| Category | Service | Port | URL / Notes |
|----------|---------|------|-------------|
| **Lakehouse** | JupyterLab | 8888 | http://localhost:8888 |
| | Spark UI | 4040 | http://localhost:4040 |
| | Spark Thrift | 10000 | JDBC/ODBC |
| | MinIO API | 9000 | S3-compatible |
| | MinIO Console | 9001 | http://localhost:9001 (admin/password) |
| | Hive Metastore | 9083 | Thrift |
| | Trino | 28080 | http://localhost:28080 |
| **Streaming** | Kafka | 9092 | Broker (KRaft mode) |
| | Kafka UI | 9090 | http://localhost:9090 |
| | Apicurio Registry | 18081 | http://localhost:18081 |
| | Debezium Connect | 8083 | REST API |
| | PostgreSQL (source) | 5433 | postgres/postgres |
| **Orchestration** | Airflow | 8000 | http://localhost:8000 |
| **Governance** | OpenMetadata | 8585 | http://localhost:8585 (admin@open-metadata.org/admin) |
| **Agent** | MCP Trino | 48080 | MCP interface → Trino |
