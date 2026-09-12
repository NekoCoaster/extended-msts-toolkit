#Requires -Version 5.1
# MSTS Derailment: one patcher, optional native V2 crawl DLL.
[CmdletBinding(SupportsShouldProcess=$true)]
param([Parameter(Position=0)][Alias('Path')][string]$ExePath,
 [ValidateSet('Gui','Status','Apply','Restore')][string]$Action='Gui',
 [switch]$RemoveEndMessage,[switch]$UnlockCameras,[switch]$Crawl,[switch]$WindowFeatures,[switch]$VerboseLoading,[switch]$StartupLog,[switch]$UnlockFPS,[switch]$CrawlHUD,
 [ValidateRange(0,100)][int]$Strength=10)
$ErrorActionPreference='Stop'
$script:Specs=@{
 Timeout=@{Offset=0x1862dc;Before=[byte[]](0x74,0x16);After=[byte[]](0xeb,0x28);Title='Infinite Derailment Timeout'}
 Camera=@{Offset=0x11c98c;Before=[byte[]](0x0f,0x84,0x55,0x03,0,0);After=[byte[]](0x90,0x90,0x90,0x90,0x90,0x90);Title='Cameras After Derailment'}
}
$script:SelectedFeature="Timeout"
$script:Spec=$script:Specs.Timeout
function Set-PatchBytes([byte[]]$Bytes,$Spec,[bool]$On) {
 $value=if($On){$Spec.After}else{$Spec.Before}
 [Array]::Copy($value,0,$Bytes,$Spec.Offset,$value.Length)
}


function Get-MstsHash([byte[]]$Bytes) {
    $sha=[Security.Cryptography.SHA256]::Create()
    try { ([BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace('-','').ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function Get-MstsImage([string]$Path) {
    if ([string]::IsNullOrWhiteSpace($Path)) { throw 'Choose a train.exe file first.' }
    $item=Get-Item -LiteralPath $Path -ErrorAction Stop
    if ($item.PSIsContainer -or $item.Extension -ine '.exe') { throw 'Choose one executable (.exe) file.' }
    if ($item.Length -ne 4091953) { throw 'Unsupported executable. This patcher supports the identified MSTS Bin 1.8.052113 builds only.' }
    $b=[IO.File]::ReadAllBytes($item.FullName)
    if ($b.Length -ne 4091953) { throw 'The file changed while being read. Select it again.' }
    $normalized=[byte[]]$b.Clone()
    $states=@{}
    foreach($name in @('Timeout','Camera')) {
        $specification=$script:Specs[$name]
        $actual=[BitConverter]::ToString($b,$specification.Offset,$specification.Before.Length)
        $on=$actual -eq [BitConverter]::ToString($specification.After)
        if(-not $on -and $actual -ne [BitConverter]::ToString($specification.Before)) {throw 'Unsupported patch bytes. No changes were made.'}
        $states[$name]=$on
        Set-PatchBytes $normalized $specification $false
    }
    $patched=$states[$script:SelectedFeature]
    $laa=($b[0x116] -band 0x20) -ne 0
    $normalized[0x116]=$normalized[0x116] -band 0xdf
    $normalizedHash=Get-MstsHash $normalized
    $wide=$false
    switch ($normalizedHash) {
        '69218fce876298c684a2140c7d3925a452c47bb10037ffd8c491f65c5c0c6e7a' { }
        '1b041ecf4b2d2a7306218efa1d7418fd87dc21dc4b2d00056cb5749084fe55a4' { $wide=$true }
        default { throw 'Unrecognized executable or additional modifications. No changes were made.' }
    }
    $original=[byte[]]$b.Clone(); Set-PatchBytes $original $script:Spec $false
    $enabled=[byte[]]$original.Clone(); Set-PatchBytes $enabled $script:Spec $true
    $originalHash=Get-MstsHash $original
    $version='MSTS Bin 1.8.052113'
    if ($wide) { $version+=' Widescreen' }
    if ($laa) { $version+=' + LAA' }
    [pscustomobject]@{
        Feature=$script:SelectedFeature; TimeoutPatched=$states.Timeout; CameraPatched=$states.Camera
        Path=$item.FullName; Version=$version; Widescreen=$wide; LAA=$laa
        State=$(if ($patched) {'PATCHED'} else {'UNPATCHED'}); IsPatched=$patched
        SHA256=(Get-MstsHash $b); OriginalHash=$originalHash; PatchedHash=(Get-MstsHash $enabled)
        Backup=$item.FullName+'.msts-derailment.'+(Get-MstsHash $b).Substring(0,16)+'.bak'
    }
}

function Assert-MstsClosed([string]$Path) {
    $name=[IO.Path]::GetFileNameWithoutExtension($Path)
    # Enumerate rather than interpolate an arbitrary filename into a query.
    foreach ($p in @(Get-Process -ErrorAction Stop | Where-Object { $_.ProcessName -ieq $name })) {
        try { $runningPath=$p.Path } catch { $runningPath=$null }
        if (-not $runningPath) { throw 'A matching application is running and its path cannot be checked. Close it before patching.' }
        if ([string]::Equals($runningPath,$Path,[StringComparison]::OrdinalIgnoreCase)) {
            throw 'Close this game before patching or restoring its executable.'
        }
    }
}


function Write-CheckedImage([string]$Path,[byte[]]$Bytes,[string]$ExpectedHash) {
 $desired=Get-MstsHash $Bytes
 $tmp=$Path+'.msts-'+[Guid]::NewGuid().ToString('N')+'.tmp'
 try {
  $s=[IO.File]::Open($tmp,'CreateNew','Write','None')
  try{$s.Write($Bytes,0,$Bytes.Length);$s.Flush($true)}finally{$s.Dispose()}
  if((Get-MstsHash ([IO.File]::ReadAllBytes($tmp))) -ne $desired){throw 'Temporary executable verification failed.'}
  Assert-MstsClosed $Path
  if((Get-MstsHash ([IO.File]::ReadAllBytes($Path))) -ne $ExpectedHash){throw 'The executable changed. Select it again.'}
  [IO.File]::Replace($tmp,$Path,[System.Management.Automation.Language.NullString]::Value)
  if((Get-MstsHash ([IO.File]::ReadAllBytes($Path))) -ne $desired){throw 'Executable verification failed. The backup was retained.'}
 }finally{if(Test-Path -LiteralPath $tmp){Remove-Item -LiteralPath $tmp}}
}
function Get-ToolkitRecords([string]$Path) {
 $gameDir=Split-Path -Parent $Path
 foreach($name in @('NEMT','MEDS','MSTS-Derailment')){
  $dir=Join-Path $gameDir $name;$file=Join-Path $dir 'installation.json'
  if(Test-Path -LiteralPath $file){
   $m=Get-Content -LiteralPath $file -Raw | ConvertFrom-Json
   $product=if($name -eq 'NEMT'){'NEMT'}else{'MSTS-Derailment'}
   if($m.product -ne $product -or $m.schema -ne 1){throw "Unrecognized ownership record in $name. No changes made."}
   [pscustomobject]@{Directory=$dir;Manifest=$m;Name=$name}
  }
 }
}
function Get-CrawlInstallation([string]$Path) {
 $records=@(Get-ToolkitRecords $Path)
 $active=@($records | Where-Object {$_.Manifest.enabled})
 if($active.Count -gt 1){throw 'Multiple enabled toolkit installations exist. Resolve the conflict before applying changes.'}
 if($active.Count){return $active[0].Manifest}
 if($records.Count){return $records[0].Manifest}
 $null
}
function Invoke-Options {
 [CmdletBinding(SupportsShouldProcess=$true)]
 param([string]$Path,[bool]$Timeout,[bool]$Camera,[bool]$CrawlMode,[ValidateRange(0,100)][int]$Thrust=10,[string]$ExpectedHash,[bool]$WindowFeatures=$false,[bool]$VerboseLoading=$false,[bool]$StartupLog=$false,[bool]$UnlockFPS=$false,[bool]$CrawlHUD=$false)
 if($CrawlMode -and -not $Timeout){throw 'Crawling requires PreventActivityEnd.'}
 $info=Get-MstsImage $Path;Assert-MstsClosed $info.Path
 if($ExpectedHash -and $ExpectedHash -ne $info.SHA256){throw 'The selected executable changed. Select it again.'}
 $gameDir=Split-Path -Parent $info.Path;$target=Join-Path $gameDir 'NEMT';$proxy=Join-Path $gameDir 'DINPUT.dll'
 $records=@(Get-ToolkitRecords $info.Path);$installed=Get-CrawlInstallation $info.Path
 $install=$Timeout -or $Camera -or $CrawlMode -or $WindowFeatures -or $VerboseLoading -or $StartupLog -or $UnlockFPS -or $CrawlHUD
 $modern=@($records | Where-Object {$_.Name -eq 'NEMT'})
 if($install -and (Test-Path -LiteralPath $target) -and -not $modern.Count){throw 'The existing NEMT folder is not owned by this installer.'}
 if(Test-Path -LiteralPath $proxy){
  if(-not $installed -or (Get-MstsHash ([IO.File]::ReadAllBytes($proxy))) -ne $installed.proxyHash){throw 'Existing DINPUT.dll is unrelated or modified. It will not be replaced.'}
 }
 # Legacy executable flags are normalized only as a one-time migration.
 $original=[IO.File]::ReadAllBytes($info.Path);$desired=[byte[]]$original.Clone()
 Set-PatchBytes $desired $script:Specs.Timeout $false;Set-PatchBytes $desired $script:Specs.Camera $false
 $desiredHash=Get-MstsHash $desired
 $payload=$null
 if($install){
  $integrity=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'runtime/integrity.json') -Raw | ConvertFrom-Json
  $payload=[IO.File]::ReadAllBytes((Join-Path $PSScriptRoot 'runtime/DINPUT.dll'))
  if((Get-MstsHash $payload) -ne $integrity.'DINPUT.dll'){throw 'Release DLL integrity mismatch.'}
 }
 foreach($record in $records){
  if($record.Name -eq 'NEMT'){continue}
  foreach($name in @('MstsCrawl.dll','crawl.js')){
   $f=Join-Path $record.Directory $name
   if((Test-Path -LiteralPath $f) -and (Get-MstsHash ([IO.File]::ReadAllBytes($f))) -ne $record.Manifest.files.$name){throw "Modified legacy payload: $name"}
  }
 }
 $printStatus='false';$centerWindowed='true'
 foreach($record in $records){
  $ini=Join-Path $record.Directory 'native.ini'
  if(Test-Path -LiteralPath $ini){
   $section=''
   foreach($line in [IO.File]::ReadAllLines($ini)){
    if($line -match '^\s*\[([^]]+)\]\s*$'){$section=$Matches[1]}
    elseif($section -ieq 'Window' -and $line -match '^\s*CenterWindowed\s*=\s*(.*?)\s*$'){$centerWindowed=if($Matches[1] -imatch '^(true|1)$'){'true'}else{'false'}}
    elseif($section -ieq 'Diagnostics' -and $line -match '^\s*WriteStatusJson\s*=\s*(.*?)\s*$'){$printStatus=if($Matches[1] -imatch '^(true|1)$'){'true'}else{'false'}}
   }
   break
  }
 }
 $backup=$info.Path+'.nemt-migration.'+$info.SHA256.Substring(0,16)+'.bak'
 if($desiredHash -ne $info.SHA256 -and (Test-Path -LiteralPath $backup) -and (Get-MstsHash ([IO.File]::ReadAllBytes($backup))) -ne $info.SHA256){throw 'Migration backup mismatch.'}
 if(-not $PSCmdlet.ShouldProcess($info.Path,'Configure native toolkit; restore known legacy executable patches if present')){return $info}
 Assert-MstsClosed $info.Path
 if((Get-MstsHash ([IO.File]::ReadAllBytes($info.Path))) -ne $info.SHA256){throw 'Executable changed during preparation.'}
 if($desiredHash -ne $info.SHA256){
  if(-not (Test-Path -LiteralPath $backup)){[IO.File]::Copy($info.Path,$backup,$false)}
  if((Get-MstsHash ([IO.File]::ReadAllBytes($backup))) -ne $info.SHA256){throw 'Backup verification failed.'}
 }
 $oldFiles=@{};$changedImage=$false;$createdDir=$false
 $names=@('DINPUT.dll')
 $paths=@($proxy)+@('native.ini','installation.json','status.json' | ForEach-Object {Join-Path $target $_})
 foreach($record in $records){$paths+=@('native.ini','installation.json','MstsCrawl.dll','MstsCrawl.config','crawl.js' | ForEach-Object {Join-Path $record.Directory $_})}
 foreach($f in ($paths | Select-Object -Unique)){$oldFiles[$f]=if(Test-Path -LiteralPath $f){[IO.File]::ReadAllBytes($f)}else{$null}}
 try{
  if($desiredHash -ne $info.SHA256){Write-CheckedImage $info.Path $desired $info.SHA256;$changedImage=$true}
  if($install){
   if(-not (Test-Path -LiteralPath $target)){[void][IO.Directory]::CreateDirectory($target);$createdDir=$true}
   $config="[Startup]`r`nVerboseLoading=$($VerboseLoading.ToString().ToLowerInvariant())`r`nWriteLog=$($StartupLog.ToString().ToLowerInvariant())`r`nUnlockFPS=$($UnlockFPS.ToString().ToLowerInvariant())`r`n`r`n[Window]`r`nEnabled=$($WindowFeatures.ToString().ToLowerInvariant())`r`nCenterWindowed=$centerWindowed`r`n`r`n[Derailment]`r`nPreventActivityEnd=$($Timeout.ToString().ToLowerInvariant())`r`nUnlockCameras=$($Camera.ToString().ToLowerInvariant())`r`nEnableCrawl=$($CrawlMode.ToString().ToLowerInvariant())`r`nCrawlStrength=$Thrust`r`n`r`n[Diagnostics]`r`nWriteStatusJson=$printStatus`r`nShowCrawlHUD=$($CrawlHUD.ToString().ToLowerInvariant())`r`n"
   [IO.File]::WriteAllText((Join-Path $target 'native.ini'),$config,(New-Object Text.UTF8Encoding($false)))
   $manifest=@{schema=1;product='NEMT';runtime='nemt-native';enabled=$true;strength=$Thrust;preventEnd=$Timeout;unlockCameras=$Camera;crawl=$CrawlMode;windowFeatures=$WindowFeatures;verboseLoading=$VerboseLoading;startupLog=$StartupLog;unlockFPS=$UnlockFPS;crawlHUD=$CrawlHUD;proxyHash=(Get-MstsHash $payload);files=@{}}
   [IO.File]::WriteAllText((Join-Path $target 'installation.json'),($manifest | ConvertTo-Json -Depth 5),(New-Object Text.UTF8Encoding($false)))
   [IO.File]::WriteAllText((Join-Path $target 'status.json'),'{"runtime":"NEMT","phase":"not-running","note":"Installer snapshot; live diagnostics are optional."}',(New-Object Text.UTF8Encoding($false)))
   [IO.File]::WriteAllBytes($proxy,$payload)
   if((Get-MstsHash ([IO.File]::ReadAllBytes($proxy))) -ne (Get-MstsHash $payload)){throw 'Installed DLL verification failed.'}
  }elseif(Test-Path -LiteralPath $proxy){Remove-Item -LiteralPath $proxy}
  foreach($record in $records){
   if($record.Name -eq 'NEMT' -and $install){continue}
   foreach($name in @('native.ini','MstsCrawl.dll','MstsCrawl.config','crawl.js')){$f=Join-Path $record.Directory $name;if(Test-Path -LiteralPath $f){Remove-Item -LiteralPath $f}}
   $record.Manifest.enabled=$false
   [IO.File]::WriteAllText((Join-Path $record.Directory 'installation.json'),($record.Manifest | ConvertTo-Json -Depth 5),(New-Object Text.UTF8Encoding($false)))
  }
  if((Get-MstsHash ([IO.File]::ReadAllBytes($info.Path))) -ne $desiredHash){throw 'Executable changed during installation.'}
 }catch{
  $problem=$_.Exception.Message
  try{
   foreach($f in $oldFiles.Keys){if($null -eq $oldFiles[$f]){if(Test-Path -LiteralPath $f){Remove-Item -LiteralPath $f}}else{[IO.File]::WriteAllBytes($f,$oldFiles[$f])}}
   if($changedImage){Write-CheckedImage $info.Path $original $desiredHash}
   if($createdDir -and @(Get-ChildItem -LiteralPath $target -Force).Count -eq 0){Remove-Item -LiteralPath $target}
  }catch{throw "$problem Rollback also failed: $($_.Exception.Message). Backup: $backup"}
  throw "$problem Changes were rolled back."
 }
 Get-MstsImage $info.Path
}

function Get-MstsRegistryPaths {
 # Read both registry views explicitly, independent of the PowerShell bitness.
 foreach($hive in @([Microsoft.Win32.RegistryHive]::CurrentUser,[Microsoft.Win32.RegistryHive]::LocalMachine)){
  foreach($view in @([Microsoft.Win32.RegistryView]::Registry32,[Microsoft.Win32.RegistryView]::Registry64)){
   $base=$null;$key=$null
   try{
    $base=[Microsoft.Win32.RegistryKey]::OpenBaseKey($hive,$view)
    $key=$base.OpenSubKey('SOFTWARE\Microsoft\Microsoft Games\Train Simulator\1.0',$false)
    if($key){foreach($name in @('EXE Path','Path')){$value=$key.GetValue($name);if($value -is [string] -and -not [string]::IsNullOrWhiteSpace($value)){$value}}}
   }catch{
    # Missing/inaccessible registry information must not prevent manual browsing.
   }finally{if($key){$key.Dispose()};if($base){$base.Dispose()}}
  }
 }
}
function Resolve-MstsStartupPath([string]$Path) {
 if(-not [string]::IsNullOrWhiteSpace($Path)){return $Path}
 $firstExisting=$null;$seen=@{}
 foreach($registered in @(Get-MstsRegistryPaths)){
  try{
   $candidate=[Environment]::ExpandEnvironmentVariables($registered.Trim().Trim('"'))
   if(-not [IO.Path]::IsPathRooted($candidate)){continue}
   if([IO.Path]::GetFileName($candidate) -ine 'train.exe'){$candidate=Join-Path $candidate 'train.exe'}
   $candidate=[IO.Path]::GetFullPath($candidate)
   if($seen.ContainsKey($candidate)){continue};$seen[$candidate]=$true
   if(-not (Test-Path -LiteralPath $candidate -PathType Leaf)){continue}
   if(-not $firstExisting){$firstExisting=$candidate}
   try{[void](Get-MstsImage $candidate);return $candidate}catch{}
  }catch{}
 }
 # Show the normal unsupported-executable result if that is all the registry offers.
 $firstExisting
}
function Show-Options([string]$InitialPath){
 Add-Type -AssemblyName System.Windows.Forms;Add-Type -AssemblyName System.Drawing
 [Windows.Forms.Application]::EnableVisualStyles()
 $form=New-Object Windows.Forms.Form;$form.Text="Neko's Extended MSTS Toolkit";$form.ClientSize=New-Object Drawing.Size(760,([Math]::Max(500,[Math]::Min(812,[Windows.Forms.Screen]::PrimaryScreen.WorkingArea.Height-70))))
 $form.StartPosition='CenterScreen';$form.FormBorderStyle='FixedDialog';$form.MaximizeBox=$false;$form.AutoScaleMode='Dpi';$form.AutoScaleDimensions=New-Object Drawing.SizeF(96,96)
 $form.Font=New-Object Drawing.Font('Segoe UI',10);$form.BackColor=[Drawing.Color]::White
 function Label-At([string]$Text,[int]$Y,[int]$Height=28){$l=New-Object Windows.Forms.Label;$l.UseMnemonic=$false;$l.Text=$Text;$l.Location=New-Object Drawing.Point(24,$Y);$l.Size=New-Object Drawing.Size(712,$Height);$form.Controls.Add($l);return $l}
 $title=Label-At "Neko's Extended MSTS Toolkit" 20 36;$title.Font=New-Object Drawing.Font('Segoe UI',17,[Drawing.FontStyle]::Bold)
 $pathText=New-Object Windows.Forms.TextBox;$pathText.ReadOnly=$true;$pathText.Location=New-Object Drawing.Point(24,69);$pathText.Size=New-Object Drawing.Size(550,28);$form.Controls.Add($pathText)
 $browse=New-Object Windows.Forms.Button;$browse.Text='Browse...';$browse.Location=New-Object Drawing.Point(585,66);$browse.Size=New-Object Drawing.Size(90,32);$form.Controls.Add($browse)
 $version=Label-At 'Choose or drop your train.exe.' 110 48;$version.Font=New-Object Drawing.Font('Segoe UI',11,[Drawing.FontStyle]::Bold)
 function Check-At([string]$Text,[int]$Y){$c=New-Object Windows.Forms.CheckBox;$c.Text=$Text;$c.Location=New-Object Drawing.Point(24,$Y);$c.Size=New-Object Drawing.Size(652,30);$form.Controls.Add($c);return $c}
 $window=Check-At 'Enable borderless (-vm:bw) and centered windowed modes' 129
 $timeout=Check-At 'Remove derailment activity-end message' 165
 $camera=Check-At 'Unlock camera modes during derailment' 201
 $crawl=Check-At 'Allow connected engines to crawl after derailment' 237
 $payloadKB=[Math]::Ceiling(((Get-Item -LiteralPath (Join-Path $PSScriptRoot 'runtime\DINPUT.dll')).Length+2048)/1024)
 $space=Label-At "Additional ~$payloadKB KB required for: DINPUT.dll, 1 folder and 3 files (native.ini, installation.json, status.json); startup.log is optional." 272 43;$space.ForeColor=[Drawing.Color]::DimGray;$space.Font=New-Object Drawing.Font('Segoe UI',9)
 $crawlHint=Label-At 'Use throttle for speed & reverser for direction' 320 25;$crawlHint.ForeColor=[Drawing.Color]::DimGray
 $sliderPanel=New-Object Windows.Forms.Panel;$sliderPanel.Location=New-Object Drawing.Point(24,352);$sliderPanel.Size=New-Object Drawing.Size(652,73);$form.Controls.Add($sliderPanel)
 $strengthLabel=New-Object Windows.Forms.Label;$strengthLabel.Text='Crawling thrust momentum:';$strengthLabel.AutoSize=$true;$sliderPanel.Controls.Add($strengthLabel)
 $strengthValue=New-Object Windows.Forms.Label;$strengthValue.AutoSize=$true;$sliderPanel.Controls.Add($strengthValue)
 $strengthBold=New-Object Drawing.Font($form.Font,[Drawing.FontStyle]::Bold)
 $slider=New-Object Windows.Forms.TrackBar;$slider.Minimum=0;$slider.Maximum=100;$slider.Value=10;$slider.TickFrequency=10;$slider.Location=New-Object Drawing.Point(20,24);$slider.Size=New-Object Drawing.Size(605,45);$sliderPanel.Controls.Add($slider)
 foreach($pair in @(@('0',0),@('100',623))){$l=New-Object Windows.Forms.Label;$l.Text=$pair[0];$l.Location=New-Object Drawing.Point($pair[1],28);$l.AutoSize=$true;$sliderPanel.Controls.Add($l)}
 $instructions="Select train.exe and choose features, then Apply. Settings take effect after restarting MSTS. Existing MEDS executable patches will be restored during migration."
 $message=Label-At $instructions 430 62
 $apply=New-Object Windows.Forms.Button;$apply.Text='Apply';$apply.Location=New-Object Drawing.Point(346,502);$apply.Size=New-Object Drawing.Size(100,34);$form.Controls.Add($apply)
 $restore=New-Object Windows.Forms.Button;$restore.Text='Uninstall';$restore.Location=New-Object Drawing.Point(454,502);$restore.Size=New-Object Drawing.Size(106,34);$form.Controls.Add($restore)
 $close=New-Object Windows.Forms.Button;$close.Text='Close';$close.Location=New-Object Drawing.Point(568,502);$close.Size=New-Object Drawing.Size(108,34);$close.Add_Click({$form.Close()});$form.Controls.Add($close)
 $credit=Label-At 'Developed and Tested by NekoCoaster, Powered by Codex - 2026 | MIT License' 550 24;$credit.ForeColor=[Drawing.Color]::DimGray;$credit.Font=New-Object Drawing.Font('Segoe UI',9)
 $github=New-Object Windows.Forms.LinkLabel;$github.Text='MEDS foundation  |  NekoCoaster/msts-extended-derailment-system';$github.Location=New-Object Drawing.Point(51,578);$github.Size=New-Object Drawing.Size(680,26)
 $github.Add_LinkClicked({Start-Process 'https://github.com/NekoCoaster/msts-extended-derailment-system'});$form.Controls.Add($github)
 $icon=New-Object Windows.Forms.PictureBox;$icon.Location=New-Object Drawing.Point(24,577);$icon.Size=New-Object Drawing.Size(20,20);$icon.SizeMode='Zoom'
 $iconPath=Join-Path $PSScriptRoot 'docs\assets\github.png'
 if(Test-Path -LiteralPath $iconPath){$icon.Image=[Drawing.Image]::FromFile($iconPath)};$form.Controls.Add($icon)
 foreach($control in $form.Controls){if($control -ne $window -and $control.Location.Y -ge 165){$control.Top+=36}}
 $window.Top=165
 foreach($control in $form.Controls){if($control.Top -ge 201){$control.Top+=96}}
 $fps=Check-At 'Unlock FPS limit (forces -noclamp launch parameter)' 201
 $verbose=Check-At 'Show verbose startup and activity loading details' 233
 $startupLogBox=Check-At 'Write startup diagnostic log (optional; NEMT\startup.log)' 265
 foreach($control in $form.Controls){if($control.Top -ge 404){$control.Top+=32}}
 $hud=Check-At 'Show crawl status in extended F5 HUD' 405
 $form.AutoScroll=$true
 $ui=@{info=$null;loading=$false}
 $refresh={ $sliderPanel.Visible=$crawl.Checked;$crawlHint.Visible=$crawl.Checked;$strengthValue.Text=if($slider.Value -eq 0){'Disabled'}else{"$($slider.Value)x"};$strengthValue.Font=if($slider.Value -eq 0){$strengthBold}else{$form.Font};$strengthValue.Location=New-Object Drawing.Point(($strengthLabel.PreferredWidth+3),0) }
 $slider.Add_ValueChanged($refresh)
 $crawl.Add_CheckedChanged({if($crawl.Checked -and -not $ui.loading){$timeout.Checked=$true};& $refresh})
 $timeout.Add_CheckedChanged({if(-not $timeout.Checked -and -not $ui.loading){$crawl.Checked=$false}})
 $load={param([string]$p)
  $ui.info=$null;$ui.loading=$true;$apply.Enabled=$false;$restore.Enabled=$false;$pathText.Text=$p
  try{$i=Get-MstsImage $p;$m=Get-CrawlInstallation $i.Path;$ui.info=$i;$pathText.Text=$i.Path;$version.Text='Valid train.exe version: '+$i.Version;$version.ForeColor=[Drawing.Color]::FromArgb(0,170,0)
   $hud.Checked=if($m -and $null -ne $m.crawlHUD){$m.enabled -and $m.crawlHUD}else{$false}
   $fps.Checked=($m -and $m.enabled -and $m.unlockFPS);$verbose.Checked=($m -and $m.enabled -and $m.verboseLoading);$startupLogBox.Checked=($m -and $m.enabled -and $m.startupLog)
   $window.Checked=if($m -and $null -ne $m.windowFeatures){$m.enabled -and $m.windowFeatures}else{$true}
   $timeout.Checked=if($m -and $m.runtime -eq 'nemt-native'){$m.enabled -and $m.preventEnd}else{$i.TimeoutPatched};$camera.Checked=if($m -and $m.runtime -eq 'nemt-native'){$m.enabled -and $m.unlockCameras}else{$i.CameraPatched};$crawl.Checked=($null -ne $m -and $m.enabled -and ($m.runtime -ne 'nemt-native' -or $m.crawl));$slider.Value=if($m){[Math]::Max(0,[Math]::Min(100,[int]$m.strength))}else{10}
   $apply.Enabled=$true;$restore.Enabled=$true;$message.ForeColor=[Drawing.Color]::DimGray;$message.Text=$instructions
  }catch{$version.Text='Unsupported executable selected. Please ensure your MSTS installation is updated to at least MSTS Bin 1.8';$version.ForeColor=[Drawing.Color]::FromArgb(204,0,0);$message.ForeColor=[Drawing.Color]::Firebrick;$message.Text=$_.Exception.Message}
  finally{$ui.loading=$false;& $refresh}
 }
 $browse.Add_Click({$d=New-Object Windows.Forms.OpenFileDialog;$d.Filter='Train executable (*.exe)|*.exe';try{if($d.ShowDialog($form) -eq 'OK'){& $load $d.FileName}}finally{$d.Dispose()}})
 $save={param([bool]$clear)
  if(-not $ui.info){return};$form.UseWaitCursor=$true;$apply.Enabled=$false;$restore.Enabled=$false;$browse.Enabled=$false
  try{$t=if($clear){$false}else{$timeout.Checked};$c=if($clear){$false}else{$camera.Checked};$r=if($clear){$false}else{$crawl.Checked};$w=if($clear){$false}else{$window.Checked}
   $result=Invoke-Options -Path $ui.info.Path -Timeout $t -Camera $c -CrawlMode $r -Thrust $slider.Value -ExpectedHash $ui.info.SHA256 -WindowFeatures $w -VerboseLoading ((-not $clear) -and $verbose.Checked) -StartupLog ((-not $clear) -and $startupLogBox.Checked) -UnlockFPS ((-not $clear) -and $fps.Checked) -CrawlHUD ((-not $clear) -and $hud.Checked) -Confirm:$false
   & $load $result.Path;$message.ForeColor=[Drawing.Color]::FromArgb(20,120,55);$message.Text=if($clear){'Toolkit removed. Widescreen and LAA were preserved.'}else{'Settings saved. Use -vm:bw for borderless or -vm:w for windowed. Restart MSTS to apply changes.'}
  }catch{$message.ForeColor=[Drawing.Color]::Firebrick;$message.Text=$_.Exception.Message}
  finally{$form.UseWaitCursor=$false;$browse.Enabled=$true;$apply.Enabled=($null -ne $ui.info);$restore.Enabled=($null -ne $ui.info)}
 }
 $apply.Add_Click({& $save $false});$restore.Add_Click({& $save $true})
 $drag={param($s,$e)if($e.Data.GetDataPresent([Windows.Forms.DataFormats]::FileDrop)){$e.Effect='Copy'}}
 $drop={param($s,$e)$files=@($e.Data.GetData([Windows.Forms.DataFormats]::FileDrop));if($files.Count -eq 1){& $load $files[0]}else{$message.Text='Drop one executable at a time.'}}
 function Enable-Drop($control){$control.AllowDrop=$true;$control.Add_DragEnter($drag);$control.Add_DragDrop($drop);foreach($child in $control.Controls){Enable-Drop $child}}
 Enable-Drop $form;& $refresh;$apply.Enabled=$false;$restore.Enabled=$false
 $form.Add_Shown({$startupPath=Resolve-MstsStartupPath $InitialPath;if($startupPath){& $load $startupPath}})
 try{[void]$form.ShowDialog()}finally{if($icon.Image){$icon.Image.Dispose()};$form.Dispose();$strengthBold.Dispose()}
}
if($MyInvocation.InvocationName -eq '.'){return}
if($Action -eq 'Gui'){Show-Options $ExePath}
elseif($Action -eq 'Status'){Get-MstsImage $ExePath;Get-CrawlInstallation $ExePath}
else{Invoke-Options -Path $ExePath -Timeout ($Action -eq 'Apply' -and $RemoveEndMessage) -Camera ($Action -eq 'Apply' -and $UnlockCameras) -CrawlMode ($Action -eq 'Apply' -and $Crawl) -VerboseLoading ($Action -eq 'Apply' -and $VerboseLoading) -StartupLog ($Action -eq 'Apply' -and $StartupLog) -UnlockFPS ($Action -eq 'Apply' -and $UnlockFPS) -CrawlHUD ($Action -eq 'Apply' -and $CrawlHUD) -Thrust $Strength -WindowFeatures ($Action -eq 'Apply' -and $WindowFeatures) -WhatIf:$WhatIfPreference}
