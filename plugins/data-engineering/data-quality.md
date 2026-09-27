# Data Quality & Governance

## Data Quality Framework

### Implementation Patterns

```python
# Example: Great Expectations-style data quality checks
expectations = [
    expect_column_values_to_not_be_null("user_id"),
    expect_column_values_to_be_between("age", 0, 150),
    expect_column_values_to_be_in_set("status", ["active", "inactive", "pending"]),
    expect_column_pair_values_A_to_be_greater_than_B("end_date", "start_date"),
    expect_table_row_count_to_be_between(1000, 10_000_000),
]
```

### Quality Gates

- **Blocking gates**: Pipeline fails if critical quality checks fail
- **Warning gates**: Pipeline continues but alerts on quality degradation
- **Trend monitoring**: Track quality metrics over time, alert on regression
- **SLA enforcement**: Escalate when data freshness exceeds thresholds

## Data Governance

### Data Classification

| Level | Examples | Controls |
|---|---|---|
| Public | Marketing content, open datasets | No restrictions |
| Internal | Employee directories, project docs | Auth required |
| Confidential | Customer PII, financial data | Encryption + audit |
| Restricted | Trade secrets, health records | Strict access, DLP |

### Privacy & Compliance

- **Data minimization**: Collect only what's needed for the stated purpose
- **Purpose limitation**: Use data only for the purpose it was collected
- **Retention policies**: Delete data when retention period expires
- **Right to erasure**: Support GDPR deletion requests across all systems
- **Anonymization**: k-anonymity, l-diversity, t-closeness for analytics
- **Pseudonymization**: Replace identifiers with tokens, maintain mapping securely

### Lineage & Observability

- **Column-level lineage**: Track transformations from source to output
- **Impact analysis**: Understand downstream effects of schema changes
- **Freshness monitoring**: Track when data was last updated
- **Anomaly detection**: Statistical monitoring for unexpected patterns
- **Data contracts**: SLAs between producers and consumers

### Access Control

- **Attribute-based (ABAC)**: Dynamic policies based on user/data attributes
- **Row-level security**: Filter data by user's permissions
- **Column masking**: Redact sensitive columns for unauthorized viewers
- **Audit logging**: Record all data access with user, time, query
- **Approval workflows**: Require sign-off for access to restricted data
