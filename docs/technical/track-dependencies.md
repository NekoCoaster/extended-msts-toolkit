# Missing route track definitions

NEMT checks route track databases once during normal startup, before MSTS loads them. If a supported text database references a section absent from both GLOBAL/tsection.dat and the route’s local dynamic definitions, it displays a dialog identifying the route and missing section, then closes MSTS when acknowledged. No Frida attachment is used.

For the known LGVMed directory, the dialog identifies Xtracks based on the author’s requirement recorded during development: LGVMed 3.0 requires Xtracks 3.10. Other routes receive a generic missing-track-definition warning directing users to their author’s README. A shared global tsection.dat can include multiple track add-ons, so this is not an installed-Xtracks version detector. It does not recommend overwriting a newer global database with an older one.

## Detection and limits

The native preflight runs outside DllMain, after executable/configuration validation, before normal loading. It reads text .tdb files and global/local section definitions; it performs no file writes. ANSI and UTF-16LE text are supported. Compressed, oversized (over 32 MiB), unreadable or unsupported data is skipped rather than guessed at. IDs are bounded below 1,048,576; nested comment blocks and tokens are bounded. Temporary definition masks occupy 256 KiB total and are freed with file buffers after checking.

TrVectorSections contains a count followed by 16 fields per vector section. The first field references the track section. Local dynamic definitions use a SectionCurve block before their ID. _Skip, _INFO and Comment blocks are excluded. A malformed vector group causes the checker to abandon that database without claiming a missing dependency.

This is a targeted safeguard, not a general route validator or crash handler. It does not verify all shape/texture files, minimum add-on versions, road databases, compressed databases or corrupt route data. Having all section IDs does not prove the full Xtracks installation is complete. An unknown route’s missing section cannot reliably identify which package supplies it. The first supported missing dependency stops startup; fix it and restart to discover another.

## Evidence

LGVMed references 544 distinct section IDs. Comparison against the VM’s stock definitions and its local dynamic definitions found 28 missing IDs; all were present in the supplied Xtracks 3.22 global definitions. The native checker found section 39870 first and displayed the Xtracks requirement before MSTS loaded the route. This follows an earlier A/B run where the unprotected installation crashed at train.exe offset 0x002f4c5a both with and without NEMT.

Unit checks exercise dynamic definitions, skipped comments, malformed groups and missing/resolved references. The same native parser is tested against the actual LGVMed text and both supplied global databases. Raw game files, Xtracks files and local backups are excluded from the package.

## VM before/after validation

Build `9d06d47e3cc9a76fd68c996bab844ff6c1cd6a19d21633faec6d291ee356ca66` displayed the missing-section dialog with stock track definitions. After backing up the 300 existing files affected by the supplied Xtracks 3.22 definitions/shapes, 3,834 package files were installed into the designated test installation. The same DLL then reached the menu with LGVMed present (400 observed startup operations, 20 display substitutions). No Frida was attached.

LGVMed subsequently generated its terrain buffers and entered the driving scene. A live loading observation showed 20.0% and approximately 11 seconds remaining; completion followed. A content-hash comparison found 464 new terrain buffers and no modified original route files. The untouched route, installation manifest and overwritten-file backups remain local under work/. Xtracks and the generated buffers remain installed in the test copy for further use. MSTS was closed normally after the HUD check.
