# Networking Patterns

## Protocol Implementation

- **State machine design**: Clear states, transitions, and timeout handling
- **Buffer management**: Pre-allocated buffer pools, zero-copy where possible
- **Fragmentation**: Handle MTU limits, reassembly with timeout
- **Flow control**: Back-pressure, sliding windows, credit-based
- **Congestion control**: AIMD, BBR, CUBIC match to use case
- **Keep-alive**: Detect dead connections before application timeout

## High-Performance Networking

- **Kernel bypass**: DPDK, XDP/eBPF for packet processing at line rate
- **io_uring**: Asynchronous I/O for high connection counts
- **Connection pooling**: Reuse connections, limit per-host connections
- **Zero-copy**: sendfile(), splice(), shared memory rings
- **Batch processing**: Process multiple packets per syscall (recvmmsg/sendmmsg)
- **NUMA awareness**: Process packets on the same NUMA node as the NIC

## SDN / Network Programmability

- **OpenFlow**: Centralized control plane, distributed data plane
- **P4**: Protocol-independent packet processing
- **gRPC/gNMI**: Network configuration and telemetry
- **YANG models**: Structured network configuration schemas
- **Intent-based networking**: Declare desired state, reconcile automatically
- **Network slicing**: Isolated virtual networks over shared infrastructure

## 5G / Telecom Patterns

- **Service-based architecture**: NFs communicate via HTTP/2, service mesh
- **Control/user plane separation**: CUPS for scalability
- **Network function virtualization**: Containerized NFs on K8s
- **Edge computing (MEC)**: Process at the network edge for low latency
- **Slice management**: Per-slice QoS, isolation, and SLA enforcement

## Reliability

- **Redundant paths**: ECMP, LAG, VRRP/HSRP for failover
- **BFD**: Bidirectional Forwarding Detection for fast failure detection
- **Graceful restart**: Maintain forwarding state during control plane restart
- **Traffic engineering**: MPLS/SR for deterministic paths
- **DDoS mitigation**: Rate limiting, scrubbing, blackhole routing
