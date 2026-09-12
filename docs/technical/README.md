# Technical documentation and testing evidence

This section records how NEMT was built and what was tested. For installation and the shipped controls, start with the [user guide](../README.md).

We develop and instrument the toolkit in a Windows VM, then test graphics and gameplay behavior on the host machine. A synthetic test, a VM observation and a host report are separate kinds of evidence. Historical hashes and timings identify the build actually tested; they are not measurements of the current package.

## Current reference

| Document | Scope |
| --- | --- |
| [Validation summary](validation.md) | First-edition evidence, known limits and unresolved coverage |
| [Native architecture](native-runtime.md) | Initialization, runtime ownership and mutation safety |
| [Crawl physics](physics.md) | Connections, engine parameters, momentum, drag and animation |
| [Activity-end and camera sites](patches.md) | Identified executable instructions |
| [Window implementation and evidence](borderless.md) | Native arguments, centering, compatibility bootstrap and historical alias |
| [Loading implementation and evidence](startup.md) | File tracing, terrain counts, estimated time and log rotation |
| [Crawl HUD implementation and evidence](crawl-hud.md) | Native font rendering, alignment and signed thrust |
| [Track dependency checker](track-dependencies.md) | Parser boundaries and LGVMed/Xtracks comparisons |
| [Movie skip implementation](startup-movie-options.md) | In-memory startup decision and retained keyboard guard |
| [Installed-file internals](installed-files.md) | Ownership, optional status output and lifecycle |
| [Build and publishing](maintenance.md) | Contributor tools, packaging and release checks |

## Investigation archive

These documents preserve development tools, experimental options, former commands and failed approaches. Their setup instructions apply to the named historical build, not automatically to the current control panel.

- [Project origins and migration](discovery.md), [migration validation](release-validation.md), and [1.0.0 checkpoint validation](release-1.0.0.md).
- [Original widescreen comparison](../investigations/widescreen-background.md), [settings and needle investigation](../investigations/settings-and-cab-needles.md), and [cab host checks](../investigations/cab-host-test.md).
- [Timing implementation](../investigations/unclamped-timing.md), [timing host checks](../investigations/timing-host-test.md), and [earlier FPS research](../miscellaneous/fps.md).
- [Red-signal message and repeat suppression](../investigations/red-signal-repeat.md) and [quality-of-life host checks](../investigations/quality-host-test.md).
- [Movie/input investigation](../investigations/startup-movie.md) and [movie renderer comparisons](../investigations/movie-window-host-test.md). Renderer experiments and the separate keyboard checkbox were retired; the delivered control skips the movie.
- [Historical release notes](../../releases/).
