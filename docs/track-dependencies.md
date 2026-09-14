# Missing route track definitions

NEMT checks supported route track databases at startup. If a route refers to a missing track-section definition, a warning identifies the route and section. Acknowledging the warning closes MSTS so the dependency can be corrected.

Read the route author's installation instructions and install the appropriate dependency. For example, LGVMed 3.0 documents an Xtracks requirement. Do not replace a newer shared track database with an older one merely because the route names an older minimum version.

Restart MSTS after resolving the missing dependency. If another dependency is missing, the next warning may identify it.

The check is automatic and makes no changes to route files. It covers supported text track databases; it is not a complete route validator, an add-on version detector or a guarantee that every required texture and shape is installed. Unsupported or unreadable data may not be checked. Follow the route's README even when no warning appears.
