# Native input and binding telemetry

This begins the previously unexamined peripheral/input surface. It reuses NEMT's established keyboard reader rather than reconstructing it from scratch. `input-bindings-summary.json` pins clean source revision5cd5896 and hashes crawl_controls.h, editor_keyboard.h and the relevant technical documents. Historical guarded-buffer and held-key tests in those documents are prior evidence, not new tests in this research session. NEMT production code is unchanged.

## Readable structures

Global008299a0 contains a circular device-list sentinel. Node+0 is next and+8 the device record. Device+4 points to an input object; input+2d is the kind byte. The known keyboard kind is1. Device+10 and+14 delimit the native keyboard table; the count is their difference, not a fixed256. Input+24 points to a bitset requiring ceil(count/8) bytes. Bit indices are native scan indices, not Windows virtual-key values, semantic command IDs or proof that an action was dispatched.

The binding table pointer is device+18. Entry address is table+(device+10+scan_index)*16. The entry has action pointer0, chained-binding pointer4, modifier word8 and flagsc. Action+0 is an opaque native identifier, +4 its listener head and+10 flags. A listener record contains callback0, context4, next8, maskc and flags10. The probe retains these records without invoking callbacks or interpreting arbitrary contexts. Global00829980 is a raw mode/gate value; zero was observed, but a complete enum is not established.

Pass193 is a reference-navigation list only. Pass194 verifies11functions934instructions2683bytes against current disk and PID7160. Lookup006bb790 traverses the list;006bb8b0 manipulates/removes bindings using16-byte entries and chained+4 pointers. Listener registration006bc130 allocates20-byte listeners and24-byte action objects and establishes callback/context/mask/flag offsets. This is structural/lifecycle evidence, not proof that a held key reaches a gameplay handler. Binding removal and deferred flags demonstrate that identity and eligibility can change with context.

The keyboard bitset and its count rule are reused from the pinned source and corroborated by the current bounded read; the native device-state producer has not yet been independently traced in this checkpoint. Nonkeyboard device internals, analog axes and the buffered-event producer remain open.

## Paused snapshot

`input-bindings-paused-01` finds two devices with raw kinds2 and1. The keyboard has238entries,30bytes, no held indices. The probe preserves73 nonempty/chained/flagged records, but only6 have an action pointer, representing5unique actions and5unique listeners through6references. Only one distinct callback address appears. These are current-context observations, not an inventory of all gameplay commands or a reason to label empty bindings unsupported.

All retained binding/action/listener rereads, keyboard/device rereads and list checks agree. Game time is paused74360.5859375 and mode0. These sequential checks cannot guarantee atomicity, exclude ABA, validate key transitions or prove eligibility under focus/menu changes. No keys were synthesized, OS-wide key state queried, commands dispatched or game memory written.

Nine candidates cover raw mode, device list/kind, keyboard count/held bits, bindings, action IDs/flags and listener records. Inventory999. The data applies to local input, not AI driver intent; an AI control value must come from AI state rather than this keyboard buffer. Further work should trace device-state updates and buffered dispatch, then validate a harmless observed key transition in a known input context. Preserve the existing gameplay tests and outstanding station/AI/origin/serializer scope.

Follow-up: INPUT-DISPATCH-FINDINGS.md supersedes the generic callback label: mask0x100 selects callback, otherwise listener+0 is a value destination. It splits action+10filter from+12stateflags, traces the keyboard bitset producer and transient event buffer, and records an existing live dispatcher detour. The first snapshot's six listener references are all callbacks. New captures preserve target_kind; original raw snapshots remain unchanged. Inventory1005; key transitions remain unvalidated.
