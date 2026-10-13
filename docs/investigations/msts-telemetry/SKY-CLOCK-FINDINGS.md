# Shader clock writer and sampled UV comparison

This refines the existing twelve CPU sky buffer candidates without adding fields. It reuses the consolidated Unity knowledge base and the immutable `sky-vertices-paused-02` capture; no new game controls or process writes were used.

## Native writer

Pass188 verifies three functions, 453 instructions and 1457 bytes against both the current executable and PID7160. Individual updater006e1470 skips a shader when selected frame+0c isFFFFFFFF. Otherwise it adds render delta00828fb4 to float32 clock+8. Zero frame duration selects index0; nonzero duration takes the native x87 conversion/adjustment path. This report does not generalize that conversion to negative or nonfinite inputs.

When the resulting index reaches frame count, the updater repeatedly subtracts frame count from the index and frame count times frame duration from the clock. The field is therefore a potentially wrapping animation phase accumulator, not a universal monotonically increasing session timer. The observed one-frame, zero-duration objects do not exercise this wrap. Malformed frame counts are not safe native-call inputs; external probes retain their bounds and never invoke this routine.

Global updater006e1520 traverses the circular list rooted at00843c94 (node+0 next, node+8 shader) and implements the same gated update. Live membership of the sampled sky shaders in this list has not been verified.

On the normal successful path in0053314d, call005331be updates sky through006e53c0 before call0053357c advances the shader list through006e1520. Other paths return early. The previously verified006e1310 predicts a frame with clock plus delta and changes UV/frame data without storing clock+8 itself. This establishes different update stages; it is a plausible contributor to sample residuals, not proof of their exact causes.

Pass186's eight verified functions (4228 instructions,14235 bytes) identify006e1650/006e1750 as material command construction/dispatch, not the clock writer. Pass187 references to00828fb4 supplied navigation only. Keep this rejected lead to avoid repeating it.

## Offline comparison

`analyse_sky_scroll.py` records the source SHA256 and compares adjacent samples only when object/buffer identities, selected frame, frame payload and vertex count agree and endpoint header checks are stable. It excludes60 unavailable-frame pairs and10 unstable-endpoint pairs. These filters do not make vertex payloads atomic or exclude ABA.

Both moving layers have stored V scroll0.004999999888241291; U is zero. Errors below use only nonzero-scroll axes, avoiding dilution by static U values:

| Layer | Eligible pairs | Vertices per pair | Median absolute UV error using shader-clock differences | Median using wall-time differences |
| --- | ---: | ---: | ---: | ---: |
| 0 | 56 | 41 | 0.000049152373776450986 | 0.000020171035528784593 |
| 2 | 58 | 73 | 0.00004882812390860636 | 0.000019237736410981096 |

Maximum absolute errors are0.0000761794472055044 for shader-clock differences and0.00005224279969168449 for wall-time differences. Static layer1/satellite1 yield zero errors but cannot discriminate clocks. Satellite0 has no available selected frame and is excluded.

This is sampled interval arithmetic, not a replay of native per-frame float32 accumulation. Sequential reads, update ordering and quantization remain relevant. Wall-time residuals happen to be smaller here; that does not prove wall time is the native producer, establish universal equivalence, or justify a correction factor. UV units are not pixels. Animated multi-frame transitions, wrap boundaries, reloads and active gameplay sky changes remain unvalidated.

The inventory stays971. This checkpoint strengthens semantics rather than completeness; broader discovery obligations inDISCOVERY-COVERAGE.md remain open.
