param([string]$BaseExe,[string]$WidescreenExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Join-Path (Split-Path $PSScriptRoot) 'legacy') 'NEMT.ps1')
foreach($source in @($BaseExe,$WidescreenExe)){
 $dir=Join-Path $Scratch ([guid]::NewGuid().ToString('N'));New-Item -ItemType Directory -Force $dir|Out-Null
 $exe=Join-Path $dir 'train.exe';Copy-Item -LiteralPath $source -Destination $exe;$hash=Get-MstsHash ([IO.File]::ReadAllBytes($exe))
 foreach($cap in @($false,$true)){
  Invoke-Options $exe $false $false $false -UnlockFPS $true -LimitToVSync $cap -Confirm:$false|Out-Null
  $ini=Get-Content (Join-Path $dir 'NEMT/settings.ini') -Raw
  $manifest=Get-Content (Join-Path $dir 'NEMT/installation.json') -Raw|ConvertFrom-Json
  if(-not $ini.Contains(('LimitToVSync='+$cap.ToString().ToLowerInvariant())) -or $manifest.limitToVSync -ne $cap){throw 'Cap setting/manifest mismatch'}
  if(-not $ini.Contains('WriteLog=false')){throw 'Logging unexpectedly enabled'}
 }
 Invoke-Options $exe $false $false $false -Confirm:$false|Out-Null
 if(Test-Path (Join-Path $dir 'DINPUT.dll')){throw 'Uninstall failed'}
 if((Get-MstsHash ([IO.File]::ReadAllBytes($exe))) -ne $hash){throw 'EXE changed'}
}
'PASS display-cap on/off config and manifest, logging default off, uninstall and unchanged base/widescreen EXEs.'
