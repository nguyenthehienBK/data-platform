# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is an on-premise data platform with the following components:

```
┌─────────────────┐     ┌─────────────────────────────┐     ┌─────────────────┐
│   Ingestion     │────▶│        Lakehouse            │────▶│   Consumption   │
│   (Debezium)    │     │  Spark/Hudi/MinIO + Trino   │     │   (dbt)         │
└─────────────────┘     └─────────────────────────────┘     └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streaming     │     │   Governance    │     │   Orchestration │
│   (Kafka)       │     │   (OpenMetadata)│     │   (Airflow)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

**Data Flow:**
1. **Stream** (PostgreSQL → Debezium → Kafka) captures CDC events
2. **Lakehouse** (Spark + Hudi + MinIO) stores data in Hudi tables on S3-compatible storage
3. **Trino** (in lakehouse compose) queries Hudi tables via Hive Metastore
4. **dbt** transforms bronze → silver → gold via Cosmos Airflow integration
5. **OpenMetadata** provides data governance and lineage

## Key Components

### 1. Lakehouse (`/lakehouse`)
Primary data storage, processing, and query engine.
- **Services:** Spark-Hudi, MinIO, Hive Metastore ×3 (HA, PostgreSQL-backed), Trino, mc (MinIO init)
- **JupyterLab:** http://localhost:8888 (notebooks mounted from `notebooks/`)
- **Spark UI:** http://localhost:4040
- **MinIO Console:** http://localhost:9001 (admin/password)
- **Hive Metastore:** ports 19083, 29083, 39083 (3 instances behind `hive-metastore-1/2/3`)
- **Trino:** http://localhost:28080

### 2. Stream (`/stream`)
Streaming infrastructure with Kafka and Debezium for CDC.
- **Services:** Kafka (KRaft mode), Apicurio Registry, PostgreSQL, Debezium Connect, Kafka UI
- **Kafka UI:** http://localhost:9090
- **Apicurio Registry:** http://localhost:18081
- **Debezium uses Avro with Apicurio converters**

### 3. Airflow (`/airflow`)
Workflow orchestration using Cosmos for dbt integration.
- **Config:** `.env` file (copy from `.env.example`)
- **DAGs:** Located in `dags/`
- **dbt profile:** Mounted at `/opt/dbt/data_pipeline/profiles.yml`

### 4. dbt (`/dbt/data_pipeline`)
Data transformation layer with bronze/silver/gold models.
- **Models:** `models/bronze/` (sources), `models/silver/`, `models/gold/`
- **Profile:** `profiles.yml` connects to Spark Thrift

### 5. Governance (`/governance/open-metadata`)
Data governance with OpenMetadata.
- **UI:** http://localhost:8585 (admin@open-metadata.org/admin)

### 6. Agent (`/agent/mcp-trino`)
MCP server for Trino integration with AI tools.
- **Go application** using `mark3labs/mcp-go` and `trinodb/trino-go-client`
- **Port:** 48080 → 8080, connects to Trino at 28080
