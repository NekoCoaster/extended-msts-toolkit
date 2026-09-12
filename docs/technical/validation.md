# First-edition validation summary

This summary distinguishes the delivered feature set from the sequence of development builds. Documentation polishing changes no runtime behavior and is not a fresh test of every feature.

| Area | Recorded evidence | Practical limit |
| --- | --- | --- |
| Installation and removal | Supported executable variants, option combinations, ownership checks, unchanged executable bytes and removal tested during development. Final movie-option installer checks passed. | Other executable modifications remain unsupported. |
| Borderless windows | Host testing covered repeated activity transitions, Alt+Tab and resolution changes. Synthetic tests cover dimensions, placement and compatibility-import chaining. | Not every monitor, DPI or graphics-wrapper configuration was tested. |
| Derailment controls and crawling | Host testing covered the native toolkit, electric/diesel locomotives and steam support during development. Equations and bounded connection handling have native tests. | Arcade behavior; logically connected cars can appear physically separated. Historical runs are not new measurements of the final DLL. |
| Extended F5 HUD | VM observations cover white-page output and both bottom anchors. Native tests cover placement, states and signed added thrust. | Other overlays can overlap it; signed nonzero force has synthetic coverage rather than an exhaustive host matrix. |
| Loading and terrain | Host terrain generation completed. VM evidence records generation counts and remaining-time text; startup tracking and log retention have automated checks. | Estimated time varies by job. No measured post-generation validation loop was identified. |
| Route dependencies | Missing LGVMed track sections detected before loading; the same test setup loaded after installing the required definitions. | Supported text databases only; this is not a full route or add-on version validator. |
| Widescreen cab dials | Host testing reported visibly improved needles. Native adapter and geometry checks passed. | Segmented needles and every custom cab were not exhaustively covered. |
| FPS/timing | Two initial host runs confirmed restored time acceleration; native timing tests exercise frame rates, multipliers and clock compensation. | Potentially unstable. The apparent improvement in 16x activity-marker messages is preliminary, not a separate confirmed fix. |
| Background audio | Native flag-change checks passed; the later broad host report covered the feature build. | The recorded per-feature guide still lacks an isolated audible test trace. |
| Red-signal continuation | Host testing confirmed the native failure popup and repeat suppression; native tests cover identity, reset and other failure reasons. | Continuing does not restore activity success. Other failures are separate. |
| Startup movie | Host testing confirmed movie skipping. Both combined-option states and unchanged executable bytes pass installer checks. | Separate keyboard recovery failed in the latest host test and is no longer offered. Movie rendering remains MSTS's responsibility. |
| Control panel | Final compact form measures 760x648, with controls within the client area and no vertical scrollbar at normal scaling. | Smaller displays and higher DPI can require scrolling. |

## Closed investigations

The first edition does not include an in-game settings page, alternate movie renderer, independent keyboard-repair checkbox, or the former borderless command alias. Their findings remain in the investigation archive. Development tools and probes are documented there solely to explain reproducibility and provenance.

## Repeating validation

Use the existing tests in the source tree and the feature-specific checklists linked from the [technical index](README.md). Record executable variant, DLL hash, settings, graphics wrapper and resolution for a live comparison. Launch MSTS normally from the intended installation; instrument only after settings and the driving scene have loaded. Keep local game files and raw research out of commits and release packages.
