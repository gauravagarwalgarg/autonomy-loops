# Network Security Patterns

## Zero Trust Architecture

- **Never trust, always verify**: Authenticate every request regardless of network location
- **Micro-segmentation**: Fine-grained access policies per workload
- **Least privilege access**: Grant minimum required network access
- **Continuous verification**: Re-authenticate on context changes (location, device, time)
- **Assume breach**: Design as if the network is already compromised

## Encryption & Authentication

- **TLS 1.3**: Minimum for all external communication
- **mTLS**: Mutual authentication for service-to-service
- **Certificate rotation**: Automated renewal before expiry (cert-manager)
- **DNSSEC**: Authenticate DNS responses
- **WireGuard/IPsec**: Encrypt east-west traffic between sites
- **Post-quantum**: Plan migration to quantum-resistant algorithms

## Firewall & Access Control

- **Default deny**: Block all traffic not explicitly allowed
- **Stateful inspection**: Track connection state for return traffic
- **Application-layer filtering**: WAF for HTTP, protocol-aware rules
- **Geo-blocking**: Restrict access by geographic origin
- **IP reputation**: Block known malicious sources
- **Microsegmentation**: Per-workload firewall policies (Calico, Cilium)

## Monitoring & Detection

- **NetFlow/sFlow**: Traffic flow analysis for anomaly detection
- **IDS/IPS**: Signature and behavioral intrusion detection
- **Packet capture**: Selective capture for forensics (tcpdump, Wireshark)
- **DNS monitoring**: Detect C2 communication, DNS tunneling
- **TLS inspection**: Decrypt and inspect encrypted traffic at boundaries
- **Honeypots**: Detect lateral movement and reconnaissance

## Incident Response

- **Automated containment**: Isolate compromised segments immediately
- **Traffic replay**: Reconstruct attack timeline from captured packets
- **IOC sharing**: STIX/TAXII for threat intelligence exchange
- **Forensic preservation**: Maintain chain of custody for evidence
