# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is an on-premise data platform with the following components:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Ingestion     │────▶│   Lakehouse     │────▶│   Consumption   │
│   (Debezium)    │     │   (Spark/Hudi)  │     │   (Trino/dbt)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streaming     │     │   Governance    │     │   Orchestration │
│   (Kafka)       │     │   (OpenMetadata) │     │   (Airflow)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Data Flow:**
1. **Stream** (PostgreSQL → Debezium → Kafka) captures CDC events
2. **Lakehouse** (Spark + Hudi + MinIO) stores data in Hudi tables on S3-compatible storage
3. **Trino** queries Hudi tables via Hive Metastore
4. **dbt** transforms raw tables into staging/marts via Cosmos Airflow integration
5. **OpenMetadata** provides data governance and lineage

## Key Components

### 1. Lakehouse (`/lakehouse`)
Primary data storage and processing with Spark, Hudi, and MinIO.
- **Entry point:** `run_spark_hudi.sh start|stop|restart`
- **JupyterLab:** http://localhost:8888 (notebooks mounted from `notebooks/`)
- **Spark UI:** http://localhost:4040
- **MinIO Console:** http://localhost:9001 (admin/password)

### 2. Stream (`/stream`)
Streaming infrastructure with Kafka and Debezium for CDC.
- **Services:** Kafka (KRaft mode), Schema Registry, PostgreSQL, Debezium Connect
- **Start:** `cd stream && docker compose up -d`

### 3. Airflow (`/airflow`)
Workflow orchestration using Cosmos for dbt integration.
- **Config:** `.env` file (copy from `.env.example`)
- **Start:** `sh start_airflow_local.sh`
- **DAGs:** Located in `dags/`
- **dbt profile:** Mounted at `/opt/dbt/data_pipeline/profiles.yml`

### 4. dbt (`/dbt/data_pipeline`)
Data transformation layer with staging and marts models.
- **Models:** `models/staging/` and `models/marts/`
- **Profile:** `profiles.yml` connects to Trino
- **Run locally:** `dbt run` / `dbt test` (requires Trino connection)

### 5. Governance (`/governance/open-metadata`)
Data governance with OpenMetadata.
- **Start:** `sh run_openmetadata.sh start`
- **UI:** http://localhost:8585 (admin@open-metadata.org/admin)

### 6. Agent (`/agent/mcp-trino`)
MCP (Model Context Protocol) server for Trino integration with AI tools.
- **Go application** using `mark3labs/mcp-go` and `trinodb/trino-go-client`
- **Start:** `docker compose up --build -d`
- **Port:** 48080 → 8080

## Service Ports Reference

| Service | Port | Notes |
|---------|------|-------|
| JupyterLab | 8888 | Lakehouse notebooks |
| Spark UI | 4040 | Spark jobs monitoring |
| Spark Thrift | 10000 | JDBC/ODBC queries |
| MinIO API/UI | 9000/9001 | S3-compatible storage |
| Trino | 28080 | SQL query engine |
| Hive Metastore | 9083 | Table metadata |
| Airflow | 8000 | Web UI |
| Kafka | 9092 | Message broker |
| Debezium | 8083 | CDC connector |
| PostgreSQL | 5432 | Source database |
| OpenMetadata | 8585 | Data governance UI |
| MCP Trino | 48080 | AI query interface |

## Common Commands

### Lakehouse
```bash
cd lakehouse
./build.sh                    # Build Docker images
./run_spark_hudi.sh start     # Start services
./run_spark_hudi.sh stop      # Stop services
docker-compose down -v        # Clean up with volumes
```

### Airflow
```bash
cd airflow
cp .env.example .env          # Configure environment
sh start_airflow_local.sh     # Start Airflow
docker compose -f docker-compose-local.yaml down  # Stop
```

### dbt (inside dbt/data_pipeline)
```bash
dbt run                       # Run all models
dbt test                      # Run tests
dbt run --select tag:mart     # Run specific tag
```

### Stream
```bash
cd stream
docker compose up -d          # Start Kafka, Debezium, Postgres
docker compose down           # Stop
```

### MCP Trino
```bash
cd agent/mcp-trino
docker compose up --build -d  # Build and start
```

## dbt Project Structure

The dbt project follows the standard layered architecture:
- `models/staging/` - Source-aligned views (`stg_*` prefix)
- `models/marts/` - Business-facing tables
- Materialization: staging = `view`, marts = `table`
- Use tags `staging` and `mart` for selective runs

## Airflow DAGs

DAGs use the Cosmos `DbtDag` integration:
- Profile config points to `/opt/dbt/data_pipeline/profiles.yml`
- Uses tags to select models: `select=["tag:mart", "tag:staging"]`
- Scheduled daily at 07:30 Asia/Ho_Chi_Minh timezone