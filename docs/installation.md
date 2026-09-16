# Install, configure and remove NEMT

## Install

Download **NEMT.zip** from the [GitHub Releases page](https://github.com/NekoCoaster/extended-msts-toolkit/releases), under **Assets**. Extract the entire ZIP and open **NEMT.exe**.

The control panel is a native 32-bit Win32 application. It does not require PowerShell, .NET, Python, WebView, or a separate GUI runtime.

Close MSTS before applying changes. The panel tries to locate MSTS automatically using the game's registry entry. Use **Browse** if the path is missing or points to another installation. You can also drag one `train.exe` onto the panel.

After the panel confirms a valid executable, select the features you want and click **Apply**. Launch the game as usual. Repeat Apply and restart MSTS whenever you change settings.

## Supported Windows versions

The native frontend is intentionally compiled against a Windows XP SP3 API baseline and is designed for:

- Windows XP SP3
- Windows 7
- Windows 10
- Windows 11

Features that rely on newer Windows APIs are capability-detected at runtime. Unsupported optional controls are disabled instead of raising the minimum operating-system requirement.

## Build from the repository ZIP

For an offline source build, the complete repository source ZIP includes the reviewed TinyCC 0.9.27 x86 compiler and required header subset at `tools\tcc\`. Keep that folder intact and double-click **BUILD AND RUN NEMT.bat**. The resulting executable is written to `build\NEMT.exe` and started automatically.

The build path is deliberately compatible with Windows XP `cmd.exe` and does not depend on CMake, Visual Studio, PowerShell, .NET, or Python.

## Supported executables

The identified MSTS Bin **1.8.052113** base, widescreen, LAA and widescreen + LAA variants are supported. NEMT checks executable contents as well as the displayed version. If another patch has changed the executable, restore a supported copy using that patch's own removal procedure before trying again.

## Common messages

| Message or symptom | What to do |
| --- | --- |
| MSTS is running | Close the simulator before Apply or Uninstall. |
| Unsupported executable | Confirm the installation and MSTS Bin version. |
| Existing DLL or ownership conflict | Check which add-on owns `DINPUT.dll`. NEMT will not overwrite an unrelated file. |
| Cab-dial checkbox is unavailable | Install the supported widescreen patch first. |
| Prefer P-cores is unavailable | The OS or CPU does not expose the required hybrid-topology APIs/classes; other NEMT functions remain available. |
| Changes do not appear | Restart MSTS and confirm you configured the installation being launched. |

For startup problems, enable **deep logging**, reproduce the problem and inspect `NEMT/startup.log`.

## Uninstall

Close MSTS, open NEMT.exe, select the installed executable and click **Uninstall**. NEMT removes its owned runtime and settings. It does not modify `train.exe` or remove unrelated graphics-wrapper files.
