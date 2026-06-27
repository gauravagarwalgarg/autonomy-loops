# Embedded Systems Standards

## Safety Standards

| Standard | Domain | Focus |
|---|---|---|
| IEC 61508 | Industrial | Functional safety of E/E/PE systems |
| ISO 26262 | Automotive | Road vehicle functional safety (ASIL A-D) |
| DO-178C | Aerospace | Software for airborne systems (DAL A-E) |
| IEC 62304 | Medical | Medical device software lifecycle |
| EN 50128 | Railway | Railway software safety (SIL 0-4) |

## Coding Standards

- **MISRA C/C++**: Mandatory for safety-critical C/C++ code
- **CERT C**: Secure coding for C systems
- **AUTOSAR C++14**: Automotive C++ coding guidelines
- **No dynamic allocation**: Forbidden in safety-critical code (heap fragmentation, non-determinism)
- **No recursion**: Stack overflow risk in resource-constrained systems
- **Fixed-width integers**: Use stdint.h types exclusively (uint8_t, int32_t, etc.)

## Resource Management

- **Stack analysis**: Verify worst-case stack depth for all tasks
- **WCET analysis**: Worst-case execution time for real-time tasks
- **Memory map**: Document RAM/ROM usage, guard against overflow
- **Interrupt latency**: Measure and bound ISR execution time
- **Power budgets**: Profile current draw per operating mode
- **Watchdog timers**: Reset system on software hang

## RTOS Patterns

- **Priority inversion**: Use priority inheritance or ceiling protocols
- **Task scheduling**: Rate-monotonic or earliest-deadline-first
- **Inter-task communication**: Message queues, semaphores, event flags
- **Critical sections**: Minimize duration, use proper guards
- **Deadline monitoring**: Detect and handle missed deadlines
- **Partition scheduling**: Time and space partitioning (ARINC 653)

## Hardware Interface Rules

- **Volatile access**: All hardware registers accessed via volatile pointers
- **Memory barriers**: Use compiler and hardware barriers for DMA/shared memory
- **Bit manipulation**: Use explicit masks and shifts, never rely on struct packing
- **Endianness**: Convert at boundaries, process in native byte order
- **Register access width**: Match access width to hardware specification
