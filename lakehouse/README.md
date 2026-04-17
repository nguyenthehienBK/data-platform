# Lakehouse — Spark + Hudi + MinIO + Hive Metastore + Trino

Docker Compose environment for data lake storage, processing, and querying.

## Services

| Service | Description |
|---------|-------------|
| **spark-hudi** | Spark 3.5 with Hudi, JupyterLab, and Hadoop AWS |
| **minio** | S3-compatible object storage (buckets: raw, bronze, silver, gold, warehouse) |
| **hive-metastore** | Hive Metastore backed by **PostgreSQL** |
| **postgres** | PostgreSQL instance for Hive Metastore persistence |
| **trino** | SQL query engine over Hudi tables |
| **mc** | MinIO client for bucket initialization |

## Quick Start

```bash
# Build images (first time)
./build.sh

# Start all services
./run_spark_hudi.sh start

# Stop
./run_spark_hudi.sh stop

# Restart
./run_spark_hudi.sh restart

# Clean up (removes volumes)
docker compose down -v
```

## Access

| Service | URL | Credentials |
|---------|-----|-------------|
| JupyterLab | http://localhost:8888 | — |
| Spark UI | http://localhost:4040 | — |
| MinIO Console | http://localhost:9001 | admin / password |
| Trino | http://localhost:28080 | — |

## Directory Structure

```
lakehouse/
├── docker-compose.yml
├── Dockerfile.spark          # Spark + Hudi + Jupyter
├── Dockerfile.hive           # Hive Metastore
├── build.sh                  # Build all images
├── run_spark_hudi.sh         # Start/stop/restart
├── conf/
│   ├── spark/                # Spark defaults
│   ├── hive/                 # Hive site config
│   ├── hudi/                 # Hudi config
│   └── trino/                # Trino catalog + JVM config
├── notebooks/                # Jupyter notebooks (mounted)
│   ├── utils.py              # Shared helpers (Spark session, column rename)
│   ├── 01-mock-data.ipynb    # Static reference data loading
│   └── 02-streaming.ipynb    # CDC streaming: Kafka → Bronze Hudi
└── data/                     # Persistent data (docker-volumes, gitignored)
```

## Notebooks

### 01-mock-data.ipynb
Loads static reference data (VN30, industry, company, news, etc.) from JSON files in MinIO `raw/` bucket into Hudi COW tables in the `warehouse` database.

### 02-streaming.ipynb
Contains a reusable `start_bronze_stream()` function that:
1. Reads Avro-serialized Debezium CDC events from Kafka
2. Deserializes using Apicurio Schema Registry
3. Flattens the Debezium envelope (before/after based on CDC op)
4. Writes to partitioned Hudi COW tables in the `bronze` database

Supports two-phase bootstrap: bulk load with `maxOffsetsPerTrigger`, then steady-state streaming.

## Storage Layout

```
MinIO
├── raw/          # Source JSON files for reference data
├── bronze/       # CDC streaming tables (Hudi COW, partitioned by _ingest_date)
├── silver/       # Cleansed incremental tables (dbt-managed)
├── gold/         # Aggregated business tables (dbt-managed)
└── warehouse/    # Static reference tables
```
