# Optional P-core preference

Enable **Prefer P-cores (optional; compatibility troubleshooting)** in the patcher, then restart MSTS. It defaults off and can be used without deep logging. The setting is also available in `NEMT/settings.ini`:

```ini
[Startup]
PreferPCores=true
```

NEMT asks Windows to use the highest reported CPU performance class as the process-default CPU Set selection. It discovers the class rather than assuming that particular processor numbers are P-cores. This is a scheduling preference, not an unconditional P-core-only affinity lock: thread-specific CPU Set selections and existing hard affinity restrictions still take precedence.

The preference is confined to MSTS and ends with the process. Uncheck it and restart to return to the normal configuration. No system-wide power plan, BIOS setting or GPU preference is changed. It also applies when launching the toolset with this NEMT installation.

Windows 10/11 CPU Set APIs and distinct performance classes are required. If Windows reports only one class, no eligible performance cores within existing restrictions, or an unsupported topology, scheduling is left unchanged. This x86 implementation deliberately skips multi-group and greater-than-32-logical-processor mappings. Deep logging records the outcome and selected CPU Set IDs.

A P-core preference is a comparison test, not an established MSTS crash fix. First capture the original failure with the option off, then compare an otherwise identical run with it on. For the reported Acer crash, the concrete evidence points to graphics-device initialization; see the [graphics investigation](technical/device-initialization.md).
