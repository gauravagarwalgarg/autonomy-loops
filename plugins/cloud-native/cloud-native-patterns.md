# Cloud Native Patterns

## Twelve-Factor App Principles

1. **Codebase**: One codebase, many deploys
2. **Dependencies**: Explicitly declare and isolate
3. **Config**: Store in environment, not code
4. **Backing services**: Treat as attached resources
5. **Build/release/run**: Strictly separate stages
6. **Processes**: Stateless, share-nothing
7. **Port binding**: Export services via port binding
8. **Concurrency**: Scale out via process model
9. **Disposability**: Fast startup, graceful shutdown
10. **Dev/prod parity**: Keep environments similar
11. **Logs**: Treat as event streams
12. **Admin processes**: Run as one-off processes

## Microservices Patterns

- **Service mesh**: Istio/Linkerd for mTLS, retries, circuit breaking
- **API Gateway**: Rate limiting, auth, request routing
- **Event-driven**: Async communication via message queues (Kafka, NATS, SQS)
- **Saga pattern**: Distributed transactions via compensating actions
- **CQRS**: Separate read and write models for performance
- **Sidecar**: Attach cross-cutting concerns without modifying services
- **Strangler fig**: Incremental migration from monolith to microservices

## Kubernetes Patterns

- **Resource limits**: Always set CPU/memory requests and limits
- **Health probes**: Liveness (restart if dead), Readiness (remove from LB if not ready)
- **Pod disruption budgets**: Ensure availability during node maintenance
- **Horizontal Pod Autoscaler**: Scale on CPU, memory, or custom metrics
- **Network policies**: Default-deny, allow only required communication
- **Security contexts**: Non-root, read-only filesystem, drop capabilities
- **ConfigMaps/Secrets**: Externalize configuration, mount or inject

## Observability

- **Structured logging**: JSON format, correlation IDs, trace context
- **Distributed tracing**: OpenTelemetry with context propagation
- **Metrics**: RED method (Rate, Errors, Duration) for services
- **USE method**: Utilization, Saturation, Errors for resources
- **SLOs/SLIs/SLAs**: Define and measure service reliability targets
- **Alerting**: Alert on symptoms (user impact), not causes

## Resilience Patterns

- **Circuit breaker**: Open after N failures, half-open to test recovery
- **Retry with backoff**: Exponential backoff with jitter
- **Bulkhead**: Isolate failures to prevent cascade
- **Timeout**: Always set timeouts on external calls
- **Fallback**: Degrade gracefully when dependencies fail
- **Rate limiting**: Protect services from overload (token bucket, sliding window)
