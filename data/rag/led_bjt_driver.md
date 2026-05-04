---
source: "ProbePilot / Demo Board Manual"
topic: "LED BJT driver"
circuit_type: "bjt_switch"
trusted: true
difficulty: "beginner"
---

# LED + NPN Driver

## Expected Behavior

With a suitable base resistor from a GPIO or divider, the transistor saturates and the LED current is set by the series resistor from supply to LED to collector (topology-dependent).

## Common Faults

- Base resistor too large → transistor never turns on → LED off
- LED installed reversed
- Collector / emitter swapped
- Open ground return

## Diagnostic Procedure

Measure supply, then LED anode/cathode, then base voltage. Base should be ~0.6–0.8V above emitter when conducting.

## Measurement Strategy

Prefer **TP1 (Vin)**, **LED anode**, **TP5 (base)** sequence to localize where the chain breaks.
