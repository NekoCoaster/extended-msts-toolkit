param([string]$BaseExe,[string]$WidescreenExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot) 'NEMT.ps1')
foreach($source in @($BaseExe,$WidescreenExe)){
 $dir=Join-Path $Scratch ([guid]::NewGuid().ToString('N'));New-Item -ItemType Directory -Force $dir|Out-Null
 $exe=Join-Path $dir 'train.exe';Copy-Item -LiteralPath $source -Destination $exe;$hash=Get-MstsHash ([IO.File]::ReadAllBytes($exe))
 Invoke-Options $exe $false $false $false -PreferPCores $true -Confirm:$false|Out-Null
 $ini=Join-Path $dir 'NEMT/settings.ini'
 if(-not (Get-Content $ini -Raw).Contains('PreferPCores=true')){throw 'CPU-only install failed'}
 Invoke-Options $exe $false $false $false -StartupLog $true -Confirm:$false|Out-Null
 if(-not (Get-Content $ini -Raw).Contains('PreferPCores=true')){throw 'CPU preference lost'}
 Invoke-Options $exe $false $false $false -StartupLog $true -PreferPCores $false -Confirm:$false|Out-Null
 if(-not (Get-Content $ini -Raw).Contains('PreferPCores=false')){throw 'CPU disable failed'}
 Invoke-Options $exe $false $false $false -PreferPCores $false -Confirm:$false|Out-Null
 if(Test-Path (Join-Path $dir 'DINPUT.dll')){throw 'Uninstall failed'}
 if((Get-MstsHash ([IO.File]::ReadAllBytes($exe))) -ne $hash){throw 'EXE changed'}
}
'PASS CPU-only install, preference preservation, disable, uninstall and unchanged base/widescreen EXEs.'
