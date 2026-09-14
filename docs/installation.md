# Install, configure and remove NEMT

## Install

Download **NEMT.zip** from the [GitHub Releases page](https://github.com/NekoCoaster/extended-msts-toolkit/releases), under **Assets**. Extract the entire ZIP. Keep its contents together and use the included **NEMT.vbs** launcher.

Close MSTS before applying changes. Open the launcher, or drag your installed `train.exe` onto it. The panel tries to locate MSTS automatically when no executable is supplied. Use **Browse** if the path is missing or points to another installation.

After the panel confirms a valid executable, select the features you want and click **Apply**. Launch the game as usual. Repeat Apply and restart MSTS whenever you change settings.

**Select All** checks every enabled checkbox. It respects compatibility restrictions and leaves the thrust slider at its current value. It includes optional startup logging and the potentially unstable FPS option, so review the selections before applying.

## Supported executables

The identified MSTS Bin **1.8.052113** base, widescreen, LAA and widescreen + LAA variants are supported. NEMT checks executable contents as well as the displayed version. If another patch has changed the executable, restore a supported copy using that patch's own removal procedure before trying again.

The cab-dial correction requires a supported widescreen-patched executable. The panel's **Widescreen patch guide** link explains that prerequisite.

## Common messages

| Message or symptom | What to do |
| --- | --- |
| MSTS is running | Close the simulator before Apply or Uninstall. |
| Unsupported executable | Confirm the installation and MSTS Bin version. A different modification may make the executable unsupported. |
| No installation detected | Use Browse to select the correct `train.exe`. |
| Existing DLL or ownership conflict | Check which add-on owns `DINPUT.dll`. Do not replace an unrelated add-on's file. |
| Cab-dial checkbox is unavailable | Install the supported widescreen patch first, then select the executable again. |
| Changes do not appear | Restart MSTS and confirm you configured the installation being launched. Some gameplay features initialize after a few seconds of unpaused driving. |
| Startup movie is black or disrupts keyboard input | Enable **Skip startup movie**. |
| Missing route track definitions | Follow the [route dependency guide](track-dependencies.md). |

For other startup problems, enable **Enable deep logging**, reproduce the problem and inspect `NEMT/startup.log`. The last recorded file is not necessarily the cause. See [loading diagnostics](startup.md).

## Uninstall

Close MSTS, open NEMT.vbs, select the installed executable and click **Uninstall**. NEMT removes its owned runtime and settings. Ownership records and diagnostics may remain for reference. It does not modify `train.exe` or remove unrelated graphics-wrapper files.

## Reporting a problem

Use the [issue tracker](https://github.com/NekoCoaster/extended-msts-toolkit/issues). Include the NEMT version shown in the title bar, the detected executable variant, the selected options, and steps to reproduce. For visual issues, include your resolution and graphics-wrapper settings. Review logs before attaching them because they can contain local file paths.

## Widescreen cab option

The cab-dial checkbox is enabled only when a supported widescreen executable is detected. Otherwise it is greyed out, with download and installation-guide links on the same line. Once a supported widescreen executable is selected, that guidance is hidden. NEMT does not apply the external widescreen patch.
