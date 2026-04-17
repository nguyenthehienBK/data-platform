# dbt Data Pipeline — CRBT

Transforms CDC data from bronze Hudi tables into silver (cleansed) and gold (aggregated) layers.

## Layer Architecture

```
Bronze (CDC raw)          Silver (cleansed)             Gold (aggregated)
┌──────────────────┐     ┌──────────────────────┐     ┌───────────────────────────┐
│ postgres_public_  │     │ slv_orders           │     │                           │
│   orders         │────▶│ slv_crbt_charge_log  │────▶│ gld_crbt_daily_charge_    │
│ pg_crbt_charge_  │     │ slv_crbt_sub_coll..  │     │   summary                 │
│   log            │     │ slv_crbt_substate_log│     │                           │
│ pg_crbt_sub_coll │     └──────────────────────┘     └───────────────────────────┘
│ pg_crbt_substate │
└──────────────────┘
```

## Model Configuration

| Layer | Materialization | File Format | Strategy | Schema |
|-------|----------------|-------------|----------|--------|
| Silver | `incremental` | Hudi | merge | `silver` |
| Gold | `table` | Hudi | — | `gold` |

All models use **Hudi Copy-on-Write** tables stored on MinIO (`s3a://silver`, `s3a://gold`).

## Sources

Defined in `models/bronze/sources.yml` — references bronze Hudi tables populated by Spark Structured Streaming from Debezium CDC.

The `orders` table has freshness checks:
- Warn after 2 hours
- Error after 6 hours

## Custom Macros

- `macros/generate_schema_name.sql` — uses the custom schema name directly (e.g., `silver`, `gold`) instead of prefixing with target schema.

## Running

```bash
# Run all models
dbt run

# Run specific layer
dbt run --select tag:silver
dbt run --select tag:gold

# Run tests
dbt test
```

## Profile

Connects to Spark Thrift server (configured in `profiles.yml`).
