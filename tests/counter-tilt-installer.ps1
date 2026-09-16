param([string]$BaseExe,[string]$WidescreenExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Join-Path (Split-Path $PSScriptRoot) 'legacy') 'NEMT.ps1')
foreach($source in @($BaseExe,$WidescreenExe)){
 $dir=Join-Path $Scratch ([guid]::NewGuid().ToString('N'));[void][IO.Directory]::CreateDirectory($dir)
 $file=Join-Path $dir 'train.exe';[IO.File]::WriteAllBytes($file,[IO.File]::ReadAllBytes((Resolve-Path $source)))
 $hash=Get-MstsHash ([IO.File]::ReadAllBytes($file));$ini=Join-Path $dir 'NEMT/settings.ini'
 Invoke-Options $file $true $true $true 10 -Confirm:$false | Out-Null
 if(-not ([IO.File]::ReadAllText($ini)).Contains('CounterTilt=false')){throw 'Counter-tilt must default off'}
 foreach($enabled in @($true,$false)){
  Invoke-Options $file $true $true $true 10 -CounterTilt $enabled -Confirm:$false | Out-Null
  Invoke-Options $file $true $true $true 10 -Confirm:$false | Out-Null
  $manifest=Get-Content (Join-Path $dir 'NEMT/installation.json') -Raw | ConvertFrom-Json
  if(-not ([IO.File]::ReadAllText($ini)).Contains('CounterTilt='+$enabled.ToString().ToLowerInvariant()) -or $manifest.counterTilt -ne $enabled){throw 'Counter-tilt setting/manifest was not preserved'}
 }
 if((Get-MstsHash ([IO.File]::ReadAllBytes($file))) -ne $hash){throw 'Executable changed'}
}
'PASS counter-tilt default off, enable/disable, omitted-option preservation, manifest and immutable EXE on both variants.'
