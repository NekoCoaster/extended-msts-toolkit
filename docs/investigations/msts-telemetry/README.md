# MSTS telemetry discovery — research checkpoint

Related to [issue #7: External Telemetry and control bridge](https://github.com/NekoCoaster/extended-msts-toolkit/issues/7).

**Status: active and incomplete.** This is an independent discovery/testing phase for eventual NEMT integration. It adds no runtime integration, external protocol, transport or control input. No telemetry candidates have been ranked or selected for retention.

Start with [the findings and coverage checkpoint](CHECKPOINT.md), [the flat inventory](INVENTORY.md), and its detailed machine-readable counterpart, `inventory.json`. The current 887 entries include 293 direct-read candidates/structures, 19 derived candidates, 68 cab channels and 507 static configuration paths (474 leaf and 37 mixed paths with four overlaps). These counts are not independent verified live values. Configuration leaf cleanup and further semantic validation remain open.

The preferred activity is Marias Pass **Grain Train Through the Night** (`evegrain.act`). Completed observations include player and AI motion, a native Stop-to-Clear signal transition, physical/offscreen AI lifecycle, inactive-service stale values, track geometry, all 732 route nodes, abstract track-presence records and signal/service associations. See the individual findings documents for confidence and limitations.

## What this branch preserves

- Findings, field specifications, generated inventory, compact measured summaries and exact-image verification reports.
- Standalone Python read-only probes and analysis scripts, plus the Ghidra export helper.
- `local-evidence-manifest.json`, identifying local-only captures and native exports by relative path, size and SHA256.

Raw gameplay captures, screenshots, Ghidra projects, decompiled/native instruction exports, installed game assets and executables are not included. The two generated cab/inventory JSON files omit their embedded decompiler excerpt strings; field metadata, references and findings remain. This selection packages the evidence; it does not select telemetry fields to keep or discard.

Paths such as `captures/...`, `passNN/...`, and references to adjacent precipitation research name evidence retained in the original local workspace (`C:/dev/Codex/2026-09-10/msts-telemetry`). Their absence from this branch is intentional. A clone contains reviewable findings and probes, but cannot rerun historical-capture analyses without those inputs. Do not describe the omitted raw evidence as independently reproduced from this checkout.

## Reproduction boundaries

Probes require Windows, Python 3, a locally installed MSTS image matching their explicit SHA256 gate, and the current process ID. They open the process only for query/read access, do not inject code and never call native functions remotely. The default installation path is `C:/MSTS`. Unknown images are rejected. Use a fresh capture name; existing capture directories are not overwritten.

Example from this directory, after loading the activity and discovering the current PID:

```powershell
python read_live.py --pid <PID> --name <fresh-name> --seconds 30 --interval 0.25
python read_infrastructure.py --pid <PID> --name <another-fresh-name>
```

Analysis scripts generally refer to specifically named historical captures. `build_inventory.py` also reads installed assets and existing generated cab metadata. `export.ps1` contains the original research machine's Ghidra/JDK/project paths; configure those paths before attempting a new native export. None of these tools is part of NEMT's end-user build or runtime path.

The tested installation already had NEMT compatibility/physics modifications enabled. Live samples are asynchronous; crossing a simulation step is recorded and is not an atomic snapshot. Paused-read checks, native static tracing, gameplay transitions and independent runtime validation are distinct evidence.

## Open work

The complete outstanding scope is in CHECKPOINT.md. It includes alternate locomotive types, remaining cab channels and producer semantics, event/evaluation transitions, origin shifts, reservations and switch changes, detailed AI/vehicle systems, peripheral camera/input/audio surfaces, update cadence and overhead, and semantic cleanup of the flat inventory. The draft research PR does not complete issue #7 or the discovery goal.
