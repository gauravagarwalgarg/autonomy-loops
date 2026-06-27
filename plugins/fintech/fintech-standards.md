# FinTech Standards & Compliance

## Latency & Performance

- **Tick-to-trade latency**: Target sub-microsecond for HFT, sub-millisecond for market making
- **Zero-allocation hot paths**: No GC pauses in critical trading loops
- **Lock-free data structures**: Use CAS operations, ring buffers, SPSC queues
- **Kernel bypass**: Consider DPDK, io_uring, or Solarflare for network I/O
- **CPU pinning**: Isolate trading threads on dedicated cores
- **Pre-allocated memory pools**: No malloc in the critical path

## Compliance & Regulatory

| Framework | Requirement |
|---|---|
| PCI-DSS | Encrypt cardholder data, audit access, vulnerability scans |
| SOX | Financial reporting controls, audit trails, access reviews |
| MiFID II | Transaction reporting, best execution, algorithmic trading controls |
| Dodd-Frank | Swap reporting, clearing mandates, position limits |
| GDPR | Customer data protection, right to erasure, data minimization |
| KYC/AML | Customer verification, transaction monitoring, suspicious activity reporting |

## Risk Management Patterns

- **Circuit breakers**: Halt trading when loss thresholds exceeded
- **Position limits**: Hard caps on exposure per instrument/portfolio
- **Kill switches**: Instant cancellation of all open orders
- **Fat finger guards**: Reject orders exceeding size/price thresholds
- **Market data sanity checks**: Detect stale/corrupt price feeds
- **Reconciliation**: Continuous position reconciliation with exchange

## Data Integrity

- **Idempotent operations**: Every transaction processor must handle replays
- **Event sourcing**: Immutable audit log of all state changes
- **Double-entry bookkeeping**: Every debit has a corresponding credit
- **Precision**: Use fixed-point decimal (never floating point for money)
- **Timestamps**: Nanosecond precision, GPS-synchronized clocks

## Security

- **HSMs**: Hardware security modules for key management
- **Field-level encryption**: Encrypt PII and financial data at rest
- **Mutual TLS**: All service-to-service communication
- **API rate limiting**: Per-client, per-endpoint throttling
- **Fraud detection**: Real-time transaction scoring
