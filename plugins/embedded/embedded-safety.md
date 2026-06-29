# Embedded Safety Patterns

## Defensive Programming

- **Input range checking**: Validate all sensor inputs against physical limits
- **Plausibility checks**: Cross-validate redundant inputs
- **Default safe state**: Define and transition to safe state on any fault
- **Graceful degradation**: Maintain critical functions when non-critical systems fail
- **Assertion monitoring**: Runtime assertions that log violations without crashing in production

## Redundancy Patterns

- **Triple Modular Redundancy (TMR)**: Three independent computations, majority vote
- **Dual-channel with comparison**: Two channels must agree within tolerance
- **Watchdog monitoring**: External watchdog verifies task liveness
- **CRC/checksum protection**: Verify data integrity in memory and communication
- **ECC memory**: Error-correcting codes for radiation/bit-flip tolerance

## Verification Requirements by Safety Level

| Level | Structural Coverage | Testing | Reviews |
|---|---|---|---|
| Highest (DAL A / ASIL D / SIL 4) | MC/DC | Formal verification + testing | Independent review |
| High (DAL B / ASIL C / SIL 3) | Decision coverage | Rigorous testing | Peer review |
| Medium (DAL C / ASIL B / SIL 2) | Statement coverage | Standard testing | Self-review |
| Low (DAL D / ASIL A / SIL 1) | Basic testing | Functional testing | Optional |

## Communication Protocols

- **CAN bus**: Automotive/industrial, priority-based arbitration
- **SPI/I2C**: Inter-chip communication, master-slave
- **ARINC 429**: Avionics data bus, unidirectional
- **MIL-STD-1553**: Military avionics, deterministic bus
- **EtherCAT**: Industrial real-time Ethernet
- **MQTT/CoAP**: IoT protocols for constrained devices

## Bootloader & Update

- **Secure boot**: Verify firmware signature before execution
- **A/B partitions**: Dual-bank update with fallback
- **Rollback protection**: Anti-rollback counter in OTP
- **Delta updates**: Minimize update payload size
- **Failsafe recovery**: Hardware-triggered recovery mode
