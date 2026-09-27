# Research checkpoint validation — 26 September 2026

Branch: `research/issue-7-msts-telemetry`, based on main `5cd5896`. Research files are confined to this directory; the repository source checksum inventory is refreshed. Production source, committed runtime DLL, build entry points and version are unchanged.

Passed locally:

- All 32 checkpoint JSON files parsed; all 23 Python scripts parsed without executing live probes.
- All 735 inventory IDs unique and carrying meaning, applicability, type, units, extraction, evidence, lifecycle and limitation fields. This is a structure check, not semantic proof of every candidate.
- Source/toolchain/corresponding-source verification.
- Bundled native frontend build.
- Frontend model: 52 checks; viewport model: 104,984 cases / 998,600 assertions; native GUI/installer: 302 checks, zero failures.
- Frontend source guards: 28 checks; repository-tool tests: 29 tests.
- Frontend and committed runtime PE32/x86 import audits.
- Packaging smoke test; source manifest unchanged by packaging. No release was published.

Incomplete local gate: `TEST NEMT.bat --ci` stopped when Windows Device Guard blocked `build/high-resolution-test.exe` (exit 4551). The later native tests in that batch were not run. This is not a passed full native suite, and the policy was not bypassed or changed. Remote PR checks may provide additional evidence separately.

Historical gameplay findings and native-byte verification are documented in their individual reports. This publication check did not repeat the historical captures and does not establish complete telemetry discovery.

## Track-item follow-up

The inventory now has 750 unique entries. Updated JSON and Python sources parse successfully. Native pass36/pass37 instruction verification passed; all stored platform/siding/speed-post comparisons and common item fields agreed with the installed TDB within documented tolerances.

GitHub Actions run 36245441062 (Verify source and native frontend) completed successfully for checkpoint commit eb0e87fee5fdeca90d2e4a7437cf80c38509ed03. This is remote workflow evidence for that commit; it does not remove the local Device Guard observation or prove gameplay findings beyond their cited captures. New follow-up commit checks are separate.

## Speed-cap and track-interaction checkpoint

763 unique candidates:206 direct-read candidates/structures,16 derived,68 cab channels,473 configuration leaf paths. All51 published JSON files and28 Python scripts parsed; every inventory row has the required provenance/meaning/lifecycle/limitation fields. This verifies structure, not complete live semantics.

Source guards28 and repository-tool tests29 passed. Frontend and committed runtime PE import audits passed using the existing unchanged binaries. Native byte comparisons for passes38-47 and50-54 matched the installed disk/live process. The paused captures verified speed-cap reproduction, freight class, pickup absence and retained sound-region values; no new moving crossing/refill/hazard test was performed.

Production code and build inputs remain unchanged. The full native batch was not rerun for this research-only update: its earlier Device Guard block remains unresolved, with no bypass attempted. The initial build/model/GUI results above remain historical evidence, not new tests of this checkpoint.


## Camera, consist, cadence and configuration checkpoint

806 unique candidates:215 direct-read candidates/structures,16 derived,68 cab channels and507 configuration paths. All66 published JSON files and35 Python scripts parse. The canonical local audit checks182 evidence paths and126 unchanged asset hashes; it is tied to the unstripped local inventory hash. The publication intentionally strips embedded decompiler excerpts, so its inventory hash differs.

New evidence includes cab/front/rear/trackside/cab mode switches, exact float32 consist mass/length aggregation, a bounded pause/resume cadence test, sound-region handle lifecycle tracing and extended cab-helper limitations. Configuration coverage now retains long leaves and values beside child blocks, and correctly handles the observed anonymous annotation groups. These are evidence improvements, not keep/drop prioritization or proof of all live semantics.

363 additional local evidence files were hashed; existing manifest entries were verified unchanged. Raw captures, native exports and game assets remain local. Source guards28, repository-tool tests29 and both PE import audits passed again using unchanged binaries. No production source/build/version change or NEMT integration was made. The earlier full-native Device Guard block remains unresolved; that batch was not rerun or bypassed. GitHub run36246913033 passed for previous commit285a0ff, not for this new checkpoint.


## Activity, clock, evaluation and stored vehicle motion checkpoint

826 unique candidates:233 direct-read candidates/structures,18 derived,68 cab channels and507 configuration paths. All87 published JSON files and39 Python scripts parse. The canonical audit checks224 evidence paths and126 unchanged asset hashes; the local inventory hash differs from the publication because embedded decompiler excerpts are omitted.

Added evidence covers activity trigger/outcome semantics and finite location-condition reconstruction, independent elapsed/day clocks with installed NEMT timing patches, capped evaluation lists and installed error labels, and stored per-car motion plus loaded Durability. Empty or stopped reads are explicitly distinguished from observed transitions. Moving/reversing/AI motion, nonzero new evaluation events and broader discovery coverage remain open. Pass70/71 clock-related live mismatches and pass82 debug-call mismatch are documented; no blanket live-byte equality claim is made.

Verified4140 existing raw-evidence hashes unchanged and added1429 local-only evidence entries. Source/toolchain verification,28 source guards,29 repository-tool tests and both PE import audits passed using unchanged existing binaries. No production code, build input, version or integration changes. The earlier full-native Device Guard block remains unresolved; the batch was not rerun or bypassed. GitHub run36248751990 succeeded for the preceding2978ac2 commit; the new commit's remote checks are separate.

## Steam, electric, motion and event checkpoint — 27 September 2026

866 unique candidates:272 direct-read candidates/structures,19 derived,68 cab channels and507 configuration paths. All132 published JSON files and56 Python sources parse. The canonical audit checks313 evidence paths and126 unchanged asset hashes. Verified5569 previous raw-evidence hashes unchanged and added553 local-only entries. Publication strips embedded decompiler excerpts; its inventory hash intentionally differs from the canonical audit hash.

New evidence covers moving player/AI stored motion, shared Default parameters, steam cab/debug fields and producer cadence, electric cab/voltage/control transitions, stale electric throttle caches and event receiver routing/scalars. Steam coal-burn units have a float32 mass-delta check; AI stored acceleration stays zero despite changing speed. Electric throttle scalar1 has a nonzero runtime transition. The sampled traction gate bit does not guarantee cache freshness. Raw event bits cannot supply counts or a complete ordered history.

Pass101 has three live entry-span mismatches, separately recorded; it was an exploratory path rather than evidence that all native instructions match. Earlier pass70/71/82 exceptions remain documented. No blanket byte-equality claim follows from the newer passing targeted comparisons. Moving electric traction, event clearing, broader AI systems and the full remaining scope in CHECKPOINT.md are still open.

The full native batch remains incomplete due to the previously observed Device Guard exit4551. No policy bypass or equivalent retry is part of this documentation checkpoint. Current validation passed: source/toolchain/corresponding-source checks for507 files,28 frontend source guards,29 repository-tool tests and both existing frontend/runtime PE import audits. These are documentation/tooling checks using unchanged binaries, not new full native gameplay validation.


## Receiver lifecycle and brake systems checkpoint — 27 September 2026

887 candidates:293 direct-read candidates/structures,19 derived,68 cab and507 configuration paths.151 published JSON files and63 Python sources parse. The canonical audit checks346 evidence paths and126 unchanged asset hashes.6122 existing raw evidence hashes remain unchanged;224 entries added (6346 total). Native exports/captures remain local and inventory decompiler excerpts are stripped in publication.

Receiver-list discovery observed20 receivers,9 linked to player cars,48 declared streams, camera/distance activation changes and processing timestamps advancing while simulation remained paused. Event masks coalesce and clear; they cannot represent a complete ordered event history or prove playback. Twelve flags changed during cab/external/cab observation and all returned to baseline.

Brake observation captured1740 samples, zero reader errors, and13920 exact pressure-to-force formula comparisons. A rising pressure reference/latch transition was observed; full release/falling events, actual wheel force and AI brakes remain unverified.23 named configuration fields now have loaded native-definition mappings; two new candidates read actual auxiliary/emergency reservoir pressures. The loaded configuration values are not the live reservoir values. Six unequal-cylinder samples cannot establish physical propagation timing under sequential reads.

Previous66f5bd1 remote workflow36254778869 completed successfully. This checkpoint's new remote checks are separate. The prior full-native DeviceGuard4551 block remains unresolved; no policy bypass or equivalent retry was attempted. Production sources and binaries remain unchanged. Goal remains active and PR remains draft.

Validation passed:534 source files and complete bundled toolchain/source verified;28 frontend source guards,29 repository-tool tests and both PE import audits passed using unchanged binaries. JSON/Python parsing and diff whitespace checks passed. These checks do not prove complete discovery or replace runtime validation.

## Brake release and moving powered-car checkpoint

889 candidates:295 direct-read candidates/structures,19 derived,68 cab channels and507 configuration paths.158 published JSON files and70 Python sources parse. Canonical audit checks363 evidence paths and126 unchanged installed-asset hashes. All6346 previous raw-evidence hashes were verified unchanged;88 added (6434 total). Raw evidence remains local; publication strips embedded decompiler excerpts.

Acela brake selector modes and mode-relative fractions now have native lookup evidence. A failed release attempt is preserved separately from the successful release and settling captures. All eight cars reached zero cylinder pressure and110 pipe pressure; a12.9296875 simulation-second capture gap prevents claiming exact time to zero. The pressure-event reference retained a nonzero residual despite zero cylinder pressure.

Moving electric capture:1182 samples, zero reader errors, positive force/current under released brakes and zero outputs while subsequently coasting. Paired-powered-car capture:875 samples, zero errors, identical front/rear stored force and power, rear current always zero and rear sampled gate bit clear. Neither rear current nor the lead gate interpretation can be generalized to independent per-car measurements. Shared force ramp native tracing retains the unusual car-field predicate, asymmetric time factors and untested reverse behavior; no claim of actual wheel-rail force or AI validation.

Validation:548 source files and complete bundled toolchain/source verified;28 source guards,29 repository-tool tests and both existing-binary PE import audits passed. Production code and binaries remain unchanged. Previous e695189 remote workflow36256558628 succeeded. New commit checks are separate. The earlier full native Device Guard4551 block remains unresolved; no equivalent retry or bypass was attempted. The full discovery goal remains active and incomplete.

## AI service and station records checkpoint

895 candidates:301 direct-read candidates/structures,19 derived,68 cab channels and507 configuration paths.180 published JSON files and77 Python sources parse. Canonical audit checks390 evidence paths and126 unchanged installed-asset hashes.6434 previous raw-evidence hashes verified unchanged;376 added (6810 total). Raw captures/native exports remain local and embedded decompiler excerpts remain omitted.

AI service400005 was observed with22 physical cars and changing speed while sampled brake-force/cylinder/traction/power fields remained zero, including the stable-read subset. The capture includes666 failure-alert paused samples after the player passed a red signal; it is not uninterrupted120-second gameplay or evidence of successful signal clearance.47 consecutive one-second AI service speed calculations matched final float32 values using target-capped integration. This is not independently measured vehicle acceleration.

Native source tracing resolves baseline versus selected-record efficiency and the installed baseline clamp helper. Morning in Maryland provides two populated player station records: platform/skip/efficiency match, while live path distances differ slightly from text declarations. Scheduled arrival/departure assignments and merge rules are traced separately from recorded event times. Recorded arrival can be synthesized from scheduled arrival. Departure/selection transitions and AI stop-time applicability remain open.

Validation passed:582 source files and bundled toolchain/corresponding source verified;28 frontend guards,29 repository-tool tests and both unchanged-binary PE import audits. Previous9f9d445 remote workflow36257858496 passed; new commit checks are separate. The earlier full-native Device Guard4551 block remains unresolved; no equivalent retry or bypass. No production code, binaries, version, protocol or runtime integration changed. Goal active, discovery incomplete, PR draft.

## Station transitions and coupling/motion interpretation checkpoint

902 candidates:304 direct-read structures/fields,23 derived,68 cab channels,507 configuration paths.193 published JSON files and83 Python sources parse. Canonical audit covers409 evidence paths and126 unchanged original-asset hashes.6810 prior raw-evidence hashes verified unchanged;296 added,7106total. Raw exports/captures remain local;embedded decompiler excerpts remain stripped.

Station cue flags cross a scheduled departure while actual departure remains unset. Identity-based successor semantics and null ambiguity are traced;boarding/departure/next-stop transitions remain unvalidated. Coupling endpoint geometry/velocity helpers are traced and paused geometry read;derived endpoint velocity is not yet a validated trajectory derivative. Preserved moving player/AI captures change orientation with zero stored angular velocity. Native AI placement resets angular momentum before recomputing angular velocity. Player position/velocity discrepancies remain with either simulation or wall time;no correction factor or stock-physics conclusion follows.

Validation:603 source files and bundled toolchain/source verified;28 frontend guards,29 repository-tool tests,both unchanged-binary PE import audits and whitespace checks passed. Previous651591a remote workflow36259730661 succeeded. New commit checks are separate. Earlier full-native Device Guard4551 block remains unresolved;no retry or bypass. No production code or binaries changed. Goal active,incomplete;PR remains draft.

## Combined motion and connection derivative checkpoint

902candidate IDs/counts preserved;418local evidence paths and126unchanged asset hashes verified. All197published JSON files and86Python files parse.7131raw evidence files are hashed in the manifest;7106prior files verified unchanged before adding25. Targeted assertions confirm motion-specific references remain on connection candidates and do not propagate to simulation.time. Shared evidence-list aliasing was corrected. Whitespace check passes. Production sources unchanged;earlier full-native DeviceGuard block remains unresolved and was not retried. These checks do not validate every telemetry meaning or complete discovery.

## Independent physics time checkpoint

909unique candidates,430local evidence paths,126unchanged original asset hashes.203published JSON files and87Python files parse. Raw manifest verifies7131old files unchanged and adds84(7215total). Matched connection comparisons preserve1692player/1649AIpairs and identical source SHA under both clocks. New native passes163/164/165 match disk/live across6313instruction bytes.1296sample moving capture has0reader errors;physics-time player agreement improves while AIabsolute movement worsens. Numerical agreement is contextual evidence,not universal telemetry accuracy or complete discovery. Source checksum/toolchain checks and whitespace reviewed for this research-only checkpoint;production files unchanged. Historical full-native DeviceGuard block remains unresolved,not retried or bypassed.

## Infrastructure associations and AI presence producer checkpoint

914 unique candidates:316 direct fields/structures,23 derived,68 cab channels,507 configuration paths.216 published JSON files and91 Python sources parse. Canonical audit verifies455 evidence paths and126 unchanged original asset hashes. Raw manifest preserves7215 previous hashes and adds728 files (7943 total),including native exports,reference queries and read-only captures;all7943 hashes were then rechecked. Raw evidence and decompiler output remain local.

A241-sample within-node AI capture has0read errors and moving presence distances,but no sampled claim,signal or branch transitions. Typed native acquisition/release paths are now traced. A paused22-car AI presence/physical distance discrepancy matches reconstructed native extrapolation within0.000342m;one sample and sorted multisets do not establish universal correction or per-car identity. The physical refresh call follows physics integration on a gated branch;complete list ownership and scheduler ordering remain open. Latest pass179 verifies735instructions2814bytes exactly against disk/live.

Source/toolchain and whitespace checks apply to this research-only checkpoint. Older frontend/repository/PE results are historical,not rerun here. The full-native DeviceGuard4551 block remains unresolved and was not retried or bypassed. Production code,binaries and assets remain unchanged;PR draft,issue7 and full discovery goal remain open.

## Identity, physicalization and route-clearance checkpoint

920unique candidates:321direct fields/structures,24derived,68cab channels,507configuration paths.224published JSON files and98Python sources parse. Canonical audit verifies475 evidence paths and126 unchanged original assets. Raw manifest verifies7943 prior hashes unchanged and adds87 files (8030total);all8030 were rechecked after synchronization.

261sample identity series captures physical AI removal with abstract records persisting. Native distance-gate inputs and1400m threshold are traced/read. A separate421sample stationary-player run has0errors and22same-identity AIpresence crossings300->310,count22conserved,followed by typed release,player acquisition,junction branch and signal changes. Paused forward head joins to databaseitem318 and the same-run0->7 transition. The iterator itself was not continuously captured. An earlier red-signal approach failure and intentionally interrupted300sample capture are retained;the successful run does not erase that failed experiment. No player crossing is claimed.

Source/toolchain and whitespace checks apply to this research-only checkpoint. Pass180 verifies501instructions1904bytes against disk/live. Previous frontend/repository/PE checks are historical,not rerun. The historical full-native DeviceGuard4551 block remains unresolved and was not retried or bypassed. No production code,binaries,protocols or original assets changed. PR remains draft;discovery and broader validation remain incomplete.

## Paired stationary monitor and physical-removal checkpoint

Inventory remains 920; canonical audit passes for 475 evidence paths and 126 unchanged original assets. All 227 published JSON files and 99 Python sources parse. The manifest verifies 8030 prior raw files unchanged and adds 27, totaling 8057. A 601-sample paired capture has zero outer/nested errors, 601 unique forward-head joins with no aspect disagreements, and one physical train/car count transition from 2/45 to 1/23. Abstract counts remain 23 player and 22 AI, with no node crossings. The player remained stationary; unsuccessful brake-release controls are documented. No moving-monitor or player-crossing validation is claimed. Final separate paused snapshot confirms clock 74360.5859375 and 23 intact player cars; the unsampled tail is explicit.

Source/toolchain and whitespace checks apply to this research checkpoint. Earlier full-native DeviceGuard4551 remains unresolved and was not retried; earlier frontend/repository/PE results are historical, not newly run. Production code and binaries are unchanged. Discovery remains active and the PR remains draft.

## Discovery-scope and metadata review

DISCOVERY-COVERAGE.md maps the original requirements to evidence and explicit remaining discovery/validation work. No completion, ranking or keep/drop decision is made. All 920 IDs retain their order and identity. Seventeen cab rows now preserve exactly the same declared unit tokens as plain strings rather than stringified lists; the body-position unit description is separately clarified. Source-manifest contents are unchanged. Signal/presence rows cite the paired series and distinguish it from the earlier AI crossing. Canonical audit passes: 480 evidence paths, 126 unchanged source assets. All 227 JSON/99 Python files parse; all 8057 old raw hashes verified unchanged, no new raw files. No game input or memory writes occurred this review. Source/toolchain and whitespace checks cover this documentation/builder checkpoint; historical native test blockage and broader discovery gaps remain unresolved.

## Environment selection and satellite parameter checkpoint

948 candidates:349 direct fields/structures,24 derived,68 cab channels,507 configuration paths. Canonical audit verifies494 evidence paths and126 unchanged original assets. All233 published JSON and103 Python sources parse. Raw manifest verifies8057 prior files unchanged and adds415 (8472total); raw captures and native exports remain local. New read-only probes preserve exact copies and hashes. The selected ENV buffer matches the native selection rule and12 loaded table entries match the explicitly named route asset. Sky structure reads3layers/2satellites with stable endpoints. Retained satellite records yield20 exact literal/default comparisons; scale/angle and light-pointer limits remain explicit.

Pass181 disk ranges match; three live spans differ in extra callers, with selection/path setup matching. Pass182 has the same one caller difference; loader/sky parser match. Pass183 twofunctions995instructions3517bytes match disk/live. Broad caller exports are not all semantically reviewed. Source/toolchain and whitespace checks cover this research-only checkpoint. Older frontend/repository/PE results are historical; full-native DeviceGuard4551 block remains unresolved and was not retried. No production code, binaries, original assets or saves changed. Goal incomplete; dynamic sky and broader discovery coverage remain open.

## Sky layer and paused render-buffer checkpoint

971 candidates (372direct24derived68cab507config),507 local evidence paths and126 unchanged original assets. Consolidated msts-unity-kb revision is pinned with consulted-file hashes and remains unchanged. Three layers/four edge records match24 scoped literal/default comparisons. Current pass184/185 instruction ranges match disk/live. Original61sample vertex series entirely failed an overstrict frame-index guard; preserved separately. Corrected preflight and61sample series succeed. All61 samples are paused at the same dayclock;layer0/2UV andfour shader clocks advance. Five shader-header rereads change,zero vertex-header changes. FFFFFFFF selected index is native parser initialization and is retained without current-frame dereference. These are CPU buffers,not proof of visible draws.

239JSON/107Python sources parse. Manifest verifies8472 prior raw files unchanged andadds57 (8529total). Source/toolchain and whitespace checks cover this research-only checkpoint; no production binaries/assets/save files changed. Historical native DeviceGuard4551 block remains unresolved/not retried; prior frontend/repository/PE tests are historical. Full discovery remains active,PR draft.

## Shader clock refinement

Inventory remains971 with513 evidence paths and126 unchanged original assets. Pass188 verifies3functions453instructions1457bytes disk/live; pass186 rejected clock-writer lead also verifies8functions4228instructions14235bytes. Offline UV comparison excludes unavailable frames and unstable endpoints and reports nonzero-scroll axes separately. Clock wrapping and update ordering are native evidence; multi-frame wrap transitions and shader-list membership are not live validated. No game controls or writes in this checkpoint.

242JSON/108Python sources parse. Raw manifest verifies8529 prior files unchanged and adds49 (8578total). Historical native-test limitations above remain unchanged; no new full native suite or remote CI result is claimed. Goal remains active and PR draft.

## Audio stream checkpoint

982 candidates (382direct25derived68cab507config);521 evidence paths and126 unchanged original assets. Pass189 sixfunctions2645instructions8915bytes match disk/live. Two paused snapshots cover33receivers67streams; first has one retained guard failure, second records256distinct nodes then a research-bound stop for that stream. Its complete queue count is unavailable;66other chains terminate. All67 second-snapshot rereads agree, without an atomicity claim. Seven native bit2 predicates are true, onlyone with a buffer pointer. AI/audio playback transitions remain unvalidated.

244JSON/110Python sources parse;8578old raw hashes unchanged,34added,8612total. No production, game-memory, asset or save changes. Historical native/remote CI limitations remain; goal active,PR draft.

## Typed and nested pending audio checkpoint

990 candidates (389direct26derived68cab507config);534 evidence paths and126 unchanged original assets. Pass190/191/192 verify5/11/5functions and2608/4254/1794instruction bytes against disk/live. Type1 payloads resolve loaded sample labels; type2 payloads require child-ring traversal returning to the wrapper. Separate paused captures preserve262top-level nodes, then12children across4wrappers and8sample identities. Two player engine streams shareone sample; no unique owner or actual playback is inferred. The traffic outer chain remains incomplete at256observed nodes.

249JSON/114Python sources parse;8612old raw hashes unchanged,94added,8706total. No game controls/process writes/assets/saves changed. Native-test limitations and remote CI status remain as above. Goal incomplete,PR draft.

## Native input and short-key checkpoint

1005 candidates (404direct26derived68cab507config),552 evidence paths and126 unchanged source assets. Reused pinned clean NEMT reader layout;238keyboard entries require30bytes. Listener targets may be callbacks or value destinations. Action filter/state words are split. Pass194 matches disk/live; pass195 matches disk withtwo live spans changed by an existing input detour. Failed pass196 function export is retained; bounded pass197/198 producer/getter ranges match disk/live.

One Shift_L press in the visible pause dialog produced two distinct native records (press/release), seen inthree of5394samples withzero read errors. Cursor/count2/2 shows both records were already consumed. Every sampled held bitset remainedzero; pause/dayclock unchanged. This demonstrates event-versus-held sampling limits, not lossless capture or gameplay dispatch. No game-memory writes/assets/save changes; UI action was one modifier press.

255JSON/119Python sources parse;8706old raw hashes unchanged,102added,8808total. Historical native-test and remote CI limitations remain above. Goal active,PR draft.


## Save-header and loaded-resource checkpoint

1015 candidates (414direct,26derived,68cab,507configuration);570evidence paths exist and126original source assets retain their hashes. Native passes201..206 match exported instruction bytes against disk/live. The46934-byte installed ASV partitions into four top-level blocks; its680-byte header partitions through file offset720. Six live session strings and four raw native Version_* words are newly inventoried. Nine distinct stored/live resource name-word pairs agree across the player/twoAI services and traffic metadata. All captured source-pointer/registry rereads agree; paused clock74360.5859375. No new save/load, UI input or process writes occurred.

268JSON/128Python sources parse. All8808previous raw-evidence hashes verified unchanged;147new raw artifacts produce8955total. Inventory audit and resource comparison pass. Native Version_* producer semantics, optional writer branches and save/load continuity remain open. The historical DeviceGuard4551 native-test limitation remains unresolved and was not retried; remote CI was not inspected. Goal active and PR draft.


## Physical save/load and observed reload checkpoint

Inventory1015 unchanged;589evidence paths/126unchanged source assets. Writer/loader/fixup passes207..216 checked;focused routines match disk/live,while213/214 include the known494bc1livepatch in main loading caller. Reused caller exports overlap. Decompiled unreachable-branch artifacts are resolved from assembly,not accepted as native behavior.

Native Save Activity created a new124746byteSAV and reload succeeded. Preserved trainID400007 and23vehicleIDs;all23caraddresses changed;positions/orientations equal. Controls preserved;postloadclock0.6875slater and tiny linear motion differences,so noexactrestorationclaim.239transitionsamples:0outerexceptions but96registryerrors(95null-address,1ownershipmismatch). No physicalAIreload validated. Researchsave retained,gamepausedinloadednotebook.

281JSON/130Python sources parse.8955prior raw hashes unchanged;269new artifacts,9224total. Generated train226rawbytes and4referenceIDs match retained source. Inventoryaudit/analyse_save_reload pass. NativeDeviceGuard4551historical limitation not retried;remoteCI not inspected. Goalactive/PRdraft.

## Moving origin and collision checkpoint

Inventory remains1015 unique candidates:414direct,26derived,68cab channels and507configuration paths. The canonical audit passes605evidence paths and126unchanged source assets. All293published JSON files and133Python sources parse. All9224previous raw-evidence hashes remain unchanged;52new entries bring the local-only manifest to9276files.

Two restarted moving runs independently observe the same origin boundary across45player/AIcars. Translation by2048metres per origin tile removes the large discontinuity. Physical section changes and monitor joins are observed; neither approach achieves successful passage of the initially red signal. The retained failure alerts are explicitly unsuccessful tests. A collision aftermath validates positive derailment/resting/angular observations and demonstrates body/track position divergence despite valid track pointers. A speed episode finalizes to one22.4140625s record on exit,corroborated by the UI's22seconds. These findings strengthen existing candidates without adding duplicate quantities.

Source/toolchain checks and staged whitespace checks are performed for this documentation/probe checkpoint. No production source or runtime build changes. The historical DeviceGuard4551 full-native-suite block remains unresolved and was not retried;remote checks for this commit are not yet inspected. This checkpoint does not claim complete discovery or close the research goal.

## Evidence access and extraction handoff

Added EXTRACTION-HANDOFF.md with the retained-evidence access recipe, supported disk build, actual per-probe guards and documented gaps, nested-error interpretation, lifecycle and time-base limitations, and fresh-capture commands. It is a working handoff; discovery and the final completion audit remain open. No new candidate quantity or game observation is claimed.

The standalone verify_evidence_manifest.py read and matched all9276published raw-evidence entries. Four offline tests passed,covering matching data and extra files,same-size corruption,missing files,and malformed manifests including duplicate/traversal paths. All293JSON and135Python sources parsed;the canonical audit still passes1015unique entries,605evidence paths and126unchanged assets. The retained research save hash matches its original capture. Production main remains clean at5cd5896. No game input or process capture was needed for this checkpoint.

## Independent physical-object registry

Inventory1018=417direct26derived68cab507configuration;609evidence paths and126unchanged assets pass the canonical audit. Added independent physical-list probe and native type/object-ID candidates. Paused snapshot contains45vehicles (4engines41wagons),all also connected to player/AItrain chains,with stable roots/node/class/table rereads and reciprocal links. No positive detached/static fixture is claimed. Corrected004a041e from allocator to method dispatcher in the load-identity report.

Pass217 verifies12functions3362instructions13153bytes andpass2184functions327instructions1038bytes against disk/live,zero mismatches/errors;overlapping exports are not unique totals. All295JSON136Python sources parse.9276priorrawhashes unchanged,63new entries=>9339retainedfiles. NoUIinput/processwrites/savechanges. FullnativeDeviceGuard4551block and uninspected currentremotechecks remain as previously documented.

## Physical registration lifecycle checkpoint

Inventory1020=419direct26derived68cab507configuration;615evidence paths and126unchanged original assets pass. Traced insertion before setup completion, parent teardown, five-list removal/count decrement and recycled list nodes. The retained paused45vehicle capture agrees with storedcount45 and all45registration bits;no actual count/bit transition or detached/static fixture was observed. Added-NoCallers exporter mode is exercised by four focused passes without changing default behavior.

All299JSON136Python sources parse.9339previous raw-evidence hashes remain unchanged;888new retained files bring the manifest to10227. Most new files are explicitly exploratory generic-helper caller exports,not independent discoveries or blanket verified native coverage. Focused byte checks and limitations are recorded in PHYSICAL-REGISTRY-LIFECYCLE.md. No production changes or full-native-suite rerun;historicalDeviceGuard4551 and uninspected current remote checks remain open.

## Five-list survey preparation and limits

Added read_manager_lists.py and MANAGER-LIST-SURVEY.md with native placement semantics and explicit unavailable-state handling. Five synthetic graph tests pass;the populated native branch remains unvalidated. New-process capture records null manager/player rather than empty lists. UI showed the preferred activity selected,but initial and recovery activation failed with 'failed to activate captured window';no successful load is claimed. User assistance was requested for foreground/start.

Pass226 verifies3functions527instructions1772bytes disk/live. Pass227 verifies4functions499instructions1577bytes,but its two generic append methods do not identify manager-list0;that inference is rejected. No new telemetry candidate. Inventory1020/615evidencepaths/126unchangedassets passes;301JSON138Pythonparse.10227priorrawhashesunchanged36new10263total. HistoricalnativeDeviceGuard4551/currentremoteCI limitations unchanged.

## Wheel, adhesion and animation sources

Inventory1024=423direct26derived68cab507configuration;625evidence paths126unchangedassets pass. Four distinct stored candidates added across the last two local research turns:ordinarywheel rate,powereddriver rate,adhesionforce limit anddriveranimation phase. Units are formula-based or explicitlyopaque;no loadedvehicle,sliptransition,animationvisualorAIupdateclaim. Context versus car definitions,Adheasion parser sorting,weatherhelperbranches and animationfactorselection are documented. Existingcabforce and externalwheelestimate are not counted again.

Pass2285functions181instructions547bytes,2292/674/2615,2301/917/3810,and2321/673/2518 matchdisk/live. Selectedconstant/token/string/vtable/thunkbytes also match. Pass231's exploratory range startsmidinstruction and is notwhole-rangedisassemblyproof.306JSON139Pythonparse;10263oldrawhashesunchanged56new10319total. NoUIretry or gameplay changes. HistoricalDeviceGuard4551/currentremoteCIlimitations unchanged.

## Wheel parameter labels and phase setup

Inventory remains1024;metadata now links the engine WheelRadius/NumWheels parser proof and Wheelset/phase initialization evidence. Audit632evidencepaths126unchangedassets passes. Selected engine dispatch/write checks32instructions157bytes and Wheelset checks18instructions83bytes matchdisk/live33612,including supporting label/table bytes. Phase setup00639549 matches92instructions329bytes. These are selected native checks,not live vehicle or rendering validation. NumWheels is retained as a native label,not inferred axle count. Declaration8c versus override90 flag propagation remains unresolved.

Publication parses309JSON141Python;10319priorrawhashesverified22new=10341total. Bounded wheel-field scan and pass233 are navigation only. Pass234 exported only00639549 after an incorrectly parsed unquoted address;no second-function verification is claimed. NoUIretry or production/gameplay changes. HistoricalDeviceGuard4551 and currentremoteCIlimitations unchanged.

## Shape animation time and callback checkpoint

Inventory1026=425direct26derived68cab507config;644evidencepaths126unchangedassetsauditpasses. Two separate current/processed shape animation scalars supplement the vehicle driverphase. Setter/callback/storage paths and lifecycle are traced,but no live vehicle/visual/AIcadence validation is claimed. Coverage review updates earlier save/reload and same-boundary origin observations without expanding them to complete fidelity or all coordinates.

Pass2351function45instructions132bytes;2361/240/684;2385/1989/5481;2394/822/2305;2401/261/708;241range44/96includingpadding matchdisk/live33612. Drivercallbacktable/labels/epsilon matched;shape vtable is liveinitialized data only. Pass237callerexports andshape-animation-references are navigation. Phase units remain unresolved;storedcurrent/processed equality is not a rendering-complete gate.

317JSON143Pythonparse;10341priorrawhashesverified156new10497total. No gameplay changes or UIretry. Productionunchanged;historicalfullnativeDeviceGuard4551 remains unresolved and currentremoteCIuninspected.

## Animation units and standalone reader

Inventory1026unchanged;652evidencepaths126unchangedassetsauditpasses. Native parser/frame-rate arithmetic and initialized zero clocks add unit/lifecycle evidence. Pass24252instructions131bytes andpass243557instructions1551bytes matchdisk/live. OpenRails format parser is separately cited only for Frame/FrameRate names. Six synthetic wheel-reader checks pass;fresh native capture reportsmanager-null/unavailable,not zero telemetry or populated-branch validation.

320JSON146Pythonparse;10497priorrawhashesverified29new10526total. Reader retains identity/reread flags andpervehicleerrors;not atomic,not ABA-proof,andnot a rendering/load-complete gate. NoUIretry or gameplay changes. HistoricalDeviceGuard4551/currentremoteCIlimitations remain unchanged.

## Populated wheel observations and resistance lead

Inventory1026 unchanged;659 evidence references and126 original asset hashes pass. Two live sequences retain130 samples,14 unpaused, with zero outer/vehicle errors or flagged identity changes. Player and AI engine rates change; adhesion and phase interpretation limits and unsampled motion tails are explicit. Five-list surveys cover23 then45 physical vehicles. User loaded the activity and authorized autonomous normal UI control; the earlier UI blocker is resolved. Last verified paused clock73877.21875.

Passes244–248 retain selected resistance/norm/CRT arithmetic with disk/live byte checks; lookup table is initialized live data. No portable resistance formula or new force candidate is claimed. Publication verifies10526 prior raw hashes and adds72 files (10598 total);327 JSON and149 Python files parse. Historical full native DeviceGuard4551 remains unresolved; current remote CI was not inspected. Production code and original assets are unchanged.

## External-view follow-up

180 samples include25 unpaused and the final paused interval. All45vehicles retained with zero read errors or flagged identity changes. Loaded car+80=1 excludes powered driver-phase bit0x800 on all four engines; Default Wheelset is nonzero. Initial diagnostic kind width was corrected from dword to byte using native assembly, with both raw attempts preserved. No visible wheel-angle or general cadence claim. Inventory1026;662 evidence paths and126 asset hashes pass. Manifest10598 prior hashes verified plus16new=10614. Publication327JSON150Python parse. Production unchanged; historical DeviceGuard4551/current remote CI limitations remain.
