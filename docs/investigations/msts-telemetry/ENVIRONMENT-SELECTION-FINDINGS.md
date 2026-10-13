# Environment selection and loaded sky enumeration

The current read-only probes identify the selected ENV filename and its native selector inputs, then enumerate the loaded sky's layers and satellites. They do not prove every field within those records has been decoded or that a selected filename is a persistent file-content identity.

## Filename selection

Native 004935af writes the UTF-16 buffer at 007b8d48. With editor override 007be0f8 nonzero it chooses `editor.env`. Otherwise season 0079a3ac in 0..3 chooses a 12-byte row of filename pointers at `[007b8d3c]+70`. Within that row weather 007be0d8=1 chooses slot2, weather2 chooses slot1, and other values choose slot0. An out-of-range season chooses offset7c regardless of weather. The latter fallback is statically observed, not recommended or runtime-tested input.

00493341 builds route, ENV and ENV texture directory buffers at 007b8310, 007b74cc and 007b76d4. The startup caller passes the selected filename to 006c34b0 and stores its returned environment at 007b6d60. The loader changes directory using its environment-directory configuration while opening the token reader, then restores directory on its successful path. A current filename buffer therefore supplies selection provenance, not an OS file-open trace or a hash of the already-loaded object.

`environment-selection-paused-01` reads season3, weather1 and editor0 at unchanged paused dayclock74360.5859375. Both selectors equal the separately stored activity-header values in this sample; their different addresses and possible lifecycle differences remain explicit. The selected and independently predicted name is `USA2snow.env`, with directories `routes\USA2\`, `routes\USA2\envfiles\` and `routes\USA2\envfiles\textures\`. Input and selected-string rereads pass.

`analyse_environment_selection.py` compares all12 loaded strings with explicitly named `C:/MSTS/ROUTES/USA2/usa2.trk` and hashes that file plus `ENVFILES/USA2snow.env`. All12 match. Every season uses the same three names here, so this comparison alone cannot independently establish season order. The script does not open a path supplied by process memory. Neither file was edited. Weather1/snow differs from slot index2; do not copy one numeric enum into the other.

## Sky structure

006e3dd0 allocates a19c-byte sky object and stores it at environment+0. It reads layer count at sky+0, initializes split+4 to -1, and when reading a count with that sentinel sets split=count-1. Layer array+8 uses stride1ac. Satellite count+180 and array+184 use stride1cd. A split override can replace the default; its drawing semantics come from the sky renderer, not the parser alone.

`sky-structure-paused-01` reads environment53729608, sky53699244, three layers, split2, layer array53760164, two satellites and satellite array53863748. Structural pointer/count rereads and both pause/clock endpoints are stable. The bounded reader preserves all three raw layer records and two raw satellite records. The bound32 is a conservative probe guard, not the native maximum. Counts describe loaded records, not visible clouds, active satellites or draw calls. No layered fade, motion, visibility or satellite trajectory is validated by this paused snapshot.

## Provenance and limits

Pass181 exports124 functions because requesting the generic string-copy wrapper also expands its callers. Do not treat that broad output as124 semantically reviewed functions. All39179instructions/159647bytes match disk; three live differences occur only in additional callers00490dac (two spans) and00494850 (one span00494bc1). The selection, directory setup and copy wrapper match live. Pass182 exports4functions/3316instructions/14309bytes, with only the same00494bc1 caller difference; loader006c34b0 and sky parser006e3dd0 match. No blanket live-binary equality is claimed. Earlier native environment reports supplied navigation and layout hypotheses; the new exported instructions and current captures supply this checkpoint's evidence.

Added candidates cover eight selection/path/table fields and six sky identity/enumeration fields. They are shared environment state, not per-train weather. Both probes are query/read-only, hash-gated to the installed image and preserve exact script copies. All jobs completed; MSTS remains paused unchanged at74360.5859375. Editor/fallback/reload/season changes, layer/satellite field semantics and dynamic sky behavior remain open. Next use the retained raw records and targeted parser/renderer functions to identify those fields; do not count undecoded raw bytes as named physical quantities.
