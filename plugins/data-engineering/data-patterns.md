# Data Engineering Patterns

## Pipeline Architecture

- **Batch processing**: Scheduled ETL with bounded data sets (Spark, dbt)
- **Stream processing**: Continuous processing of unbounded data (Flink, Kafka Streams)
- **Lambda architecture**: Batch + speed layers for completeness + freshness
- **Kappa architecture**: Stream-only with reprocessing capability
- **Medallion architecture**: Bronze (raw) → Silver (cleaned) → Gold (aggregated)
- **Event sourcing**: Immutable event log as source of truth

## Data Quality

| Dimension | Check |
|---|---|
| Completeness | No unexpected nulls, all required fields present |
| Uniqueness | No duplicate records on primary keys |
| Timeliness | Data arrives within SLA window |
| Validity | Values conform to schema and business rules |
| Consistency | Cross-system values agree |
| Accuracy | Values match real-world truth (sampled) |

## Schema Management

- **Schema registry**: Centralized schema versioning (Confluent, AWS Glue)
- **Backward compatibility**: New schema reads old data
- **Forward compatibility**: Old schema reads new data
- **Schema evolution**: Add optional fields, never remove or rename
- **Data contracts**: Producers declare schema guarantees

## ML Pipeline Patterns

- **Feature store**: Centralized feature computation and serving
- **Model registry**: Version, stage, and deploy ML models
- **Training pipelines**: Reproducible, parameterized training runs
- **A/B testing**: Controlled model comparison with statistical rigor
- **Model monitoring**: Detect drift, performance degradation, bias
- **Experiment tracking**: Log hyperparameters, metrics, artifacts (MLflow, W&B)

## Infrastructure

- **Data lakehouse**: Object storage + query engine (Delta Lake, Iceberg, Hudi)
- **Orchestration**: DAG-based scheduling (Airflow, Dagster, Prefect)
- **Compute separation**: Decouple storage from compute for elasticity
- **Data catalog**: Discovery, lineage, ownership (DataHub, OpenMetadata)
- **Cost optimization**: Partition pruning, columnar formats, tiered storage
