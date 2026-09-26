# Catalogue evidence audit

audit_inventory.py checks the canonical local catalogue for unique IDs, nonempty required metadata, existence of path-based evidence, and current hashes of the126 source assets recorded in source-manifest.json. inventory-audit.json records the inventory hash so its result is tied to a particular generated catalogue. Rebuilding inventory.json changes its generation timestamp/hash; rerun the audit afterward.

Current result:768 unique IDs, no empty required metadata,173 distinct evidence paths present,126 source hashes matching. Native cab routing dictionaries are structured evidence and are not treated as filenames. These are structural/provenance checks only; file presence does not prove the claim citing it, and unique IDs do not prove semantic uniqueness.

Corrections made during this audit:

-42 installed cab-channel rows had empty unit lists. They now explicitly say no unit was declared in the sampled CVF controls and native units remain unresolved. Empty declarations are not dimensionless units. No channel was discarded.
-The speedpost byte row still said restriction units were unresolved despite later native conversion evidence. It now describes the traced mph/km/h flag and conversion, cites the newer handler evidence, and preserves uncertainty for subtype1 and actual crossing behavior.

The earlier publication validation said every required field was present; that did not establish nonempty or complete semantics. This audit adds that distinction rather than retroactively claiming fuller validation.

Open semantic review remains substantial:473 config leaf paths may contain parser artifacts or duplicate declarations; many cab sources/units have only static evidence; native field availability depends on engine type and lifecycle. Player diesel observations do not establish equivalent steam/electric or AI systems. Extended cab aliases and no-update branches remain in the findings rather than inflating the count. Unresolved runtime tests and full discovery scope remain in README.md and individual findings. No completion, ranking or keep/drop decision follows from this audit.

Run this audit in the original workspace. The published repository deliberately lacks raw captures and native exports, so a clone alone cannot satisfy the local evidence-existence check. The audit performs no game writes or asset changes.

Follow-up: CONFIG-PARSER-FINDINGS.md corrects a leaf-length cutoff and anonymous-group nesting. The current audit now covers769 IDs; the768 result above is the earlier checkpoint. See inventory-audit.json for the current inventory hash.

Mixed-node follow-up: the current audit covers802 IDs and507 configuration paths; config-mixed-validation.json separately checks evidence for37 mixed paths and four leaf/mixed overlaps. Earlier counts above are historical checkpoints.

Evidence-list isolation correction: build_inventory.py now copies each supplied evidence list when creating a candidate. Shared list aliasing previously caused later motion-specific additions to appear on unrelated candidates and repeat on siblings. Rebuilding keeps902candidates and418distinct referenced paths,with unchanged126asset hashes;it removes unintended cross-candidate propagation rather than deleting underlying evidence. This corrects metadata association,not native field semantics.
