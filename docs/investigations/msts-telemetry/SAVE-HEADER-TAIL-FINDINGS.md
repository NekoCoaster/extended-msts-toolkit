# Save-header tail and loaded resource metadata

This follow-up completes the structural partition of the installed `evegrain.asv` SaveHeader block, ending exactly at file offset720. It supersedes the earlier prefix-only coverage statement in SAVE-HEADER-FINDINGS.md. It does not decode the full save format or validate save/load behavior.

Pass204 verifies6functions771instructions2257bytes, pass205 verifies4functions118instructions323bytes, and pass206 verifies9functions1358instructions4682bytes against both disk and live image. The verification covers exported instruction ranges, not all possible branches or target-process behavior.

`decode_save_header_tail.py` extends the retained prefix at offset163. Helper0049fda3 emits six words from offsets0,4,8,c,10,14. The stored first tuple is8,53,15,6,5,2001 and the next simulation tuple is0,0,12,0,0,0. The system date helper00645dc8 adjusts month/year via CRT-style calls, but complete component ordering and timezone semantics remain unproven. Do not label these tuples UTC timestamps. Following fields are raw word173400, camera-list indexFFFFFFFF, a44-byte simulation-clock block, three condition words0/1/1, and weather/season words0/1. Existing clock/origin/weather candidates are not duplicated.

The remaining blocks partition offsets283..720: Version_Path404c9 ends374; Version_Consist404c8 ends510; Version_Service404cb ends656; Version_Traffic404ca ends707; StaticFlags40068 ends720. Native table label/token pairs match disk/live. The first three lists use child token4026f, whose native label is TrItemSData. That reused label is not evidence that these entries describe physical track items. Each child here contains a zero label byte, a bounded length-prefixed UTF16 name, and a uint32 word. StaticFlags stores0 in this fixture.

Native helper004a0010 visits the player service00809890 and services in circular registry00809af8 only when service+130 is nonnull. Callbacks0049fe49/0049ffa1/0049ffe5 obtain path name at[path+4]/word+18, consist inline name atconsist+8/word+88, and service name at[service+8]/word+4. Consist is[service+18]. Traffic name/word come from809ae0/809ae8. Callback0049fe93 emits each name once using temporary list helpers0049ff1d/0049ff69. Exact case-comparison rules and behavior with conflicting words for equal names remain untested.

The read-only `header-resource-versions-paused-01` capture includes the player and two AI services, all with loaded path resources. Both AI services share the same path object. Registry and source-pointer rereads agree; the game remains paused at74360.5859375. `analyse_header_resource_versions.py` compares these sources to the installed ASV: all9distinct name/word pairs agree, in observed order.

| Native list | Retained name/word pairs |
|---|---|
| Version_Path | EveGrain:2; EveGrain (Traffic):1 |
| Version_Consist | Dash921gran:2; 2 x Dash 9, 20 Intermodal:2; D9gds:0 |
| Version_Service | EveGrain:9; EveGrain (Traffic):1; EveGrain (Traffic01):1 |
| Version_Traffic | EveGrain (Traffic):14 |

Four new direct candidates retain these raw resource words under their native Version_* context. The producer, increment policy, uniqueness, and relationship to asset Serial declarations remain untraced. These are not train movement counters or content hashes. Together with the six loaded session strings from the prior checkpoint, the inventory now contains1015 candidates:414direct,26derived,68cab channels,507configuration paths. Counts describe the current discovery inventory, not exhaustive completion.

The ASV predates this live session. No new save was written or loaded, and matching resource metadata does not establish round-trip state restoration. Sequential pointer rereads cannot prove atomic string/scalar contents or exclude pointer reuse. No UI input, process writes, original-asset edits or production NEMT changes occurred in this checkpoint. Next serialization questions include physical-train block fields, optional writer branches, loader fixups, and continuity after an actual save/load.
