# Research navigation

Use this page to acquire only the evidence needed for the next decision. This index is an offline navigation aid; using it does not require resuming live research.

## Source order

- Current state and boundaries: [handoff](NEW-CHAT-HANDOFF.md).
- Subsystem scope and remaining questions: [coverage matrix](DISCOVERY-COVERAGE.md).
- Candidate metadata: `inventory.json`; search by candidate ID before reading whole records. [INVENTORY.md](INVENTORY.md) is a generated listing, not the starting context.
- Native navigation: `python research_index.py <address-or-finding-topic> --limit 8`. The generated `research-function-index.json` groups all retained assembly exports by entry address, preserves every path/hash variant, and indexes finding references and literal direct CALL edges plus one-hop callers through single-jump thunks. Edges combine retained variants; compare source exports when variants differ.
- Read validity and raw evidence: [extraction handoff](EXTRACTION-HANDOFF.md), `source-manifest.json`, `local-evidence-manifest.json` in the published research folder.

## Efficient investigation loop

1. Name the question and what observation would distinguish the competing explanations.
2. Query an address or finding topic, then inspect the relevant finding paragraph and assembly range. Check existing captures and byte reports before rerunning anything.
3. Follow actual direct-call targets, including thunk functions. The index does not resolve indirect calls, infer field ownership, prove execution, or choose a universally correct decompilation.
4. If exports differ, compare the retained variants and verify relevant bytes against the current supported build. A byte-backed navigation recommendation is not a latest-version or validity claim.
5. Batch a bounded set of related writers/callers. Export only absent or inadequate evidence. Use normal gameplay/read-only sampling only for unresolved runtime questions.
6. Record conclusion, evidence, rejected hypothesis, limits and next question together. Validate changed candidate metadata; publish coherent checkpoints rather than every small inspection.

## Commands

Run from the canonical research directory:

```text
python research_index.py 005a3941 --limit 8
python research_index.py STATION --limit 12
python research_index.py MONITOR --limit 12
python research_index.py --build
```

Build scans retained named assembly files and root `*FINDINGS.md` documents. It does not read live memory, invoke Ghidra, modify raw evidence, or infer semantic coverage. Address mentions are lexical navigation leads. Rebuild after adding exports/findings. A published clone can query the generated map; building without raw exports is refused.

## History

The old [handoff](NEW-CHAT-HANDOFF-ARCHIVE-20261010.md), [coverage document](DISCOVERY-COVERAGE-ARCHIVE-20261010.md) and [README](README-ARCHIVE-20261010.md) are preserved byte-for-byte. `organization-archive-manifest.json` records their hashes. Existing finding files and older history files remain unchanged. Do not load all archives as routine context.
