---
source: "ProbePilot / Internal Lab Notes"
topic: "Op-Amp Saturation"
circuit_type: "op_amp"
trusted: true
difficulty: "intermediate"
---

# Op-Amp Saturation

## Expected Behavior

The output should track the linear region defined by supply rails minus headroom. For a 9V single-supply stage, small-signal outputs stay away from 0V and VCC.

## Formula

For an inverting gain stage: \( V_{out} \approx -\frac{R_f}{R_{in}} V_{in} \) until clipping.

## Common Faults

- Missing feedback resistor (latch-up or saturated output)
- Input beyond common-mode range
- Load drawing too much current (rail sag)

## Diagnostic Procedure

1. Measure supply pins vs ground.
2. Measure input and output DC bias.
3. Reduce input amplitude and re-check linearity.

## Measurement Strategy

Use a multimeter for DC bias, then an oscilloscope capture for clipping or oscillation.
