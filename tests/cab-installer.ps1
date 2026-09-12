param([string]$BaseExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot) 'NEMT.ps1')
$dir=Join-Path $Scratch ([Guid]::NewGuid().ToString('N'));[void][IO.Directory]::CreateDirectory($dir)
$file=Join-Path $dir 'train.exe';Copy-Item -LiteralPath $BaseExe -Destination $file
$hash=Get-MstsHash ([IO.File]::ReadAllBytes($file))
Invoke-Options $file $true $false $false -Confirm:$false | Out-Null
$ini=Join-Path $dir 'NEMT/settings.ini'
if(-not ([IO.File]::ReadAllText($ini)).Contains('CorrectNeedleAspect=false')){throw 'Experiment should default off'}
foreach($value in @('true','false')){
 $text=[IO.File]::ReadAllText($ini) -replace 'CorrectNeedleAspect=(true|false)',("CorrectNeedleAspect="+$value)
 [IO.File]::WriteAllText($ini,$text)
 Invoke-Options $file $true $true $false -Confirm:$false | Out-Null
 if(-not ([IO.File]::ReadAllText($ini)).Contains("CorrectNeedleAspect=$value")){throw 'Installer lost cab preference'}
}
Invoke-Options $file $false $false $false -Confirm:$false | Out-Null
if((Get-MstsHash ([IO.File]::ReadAllBytes($file))) -ne $hash){throw 'Executable changed'}
if(Test-Path (Join-Path $dir 'DINPUT.dll')){throw 'Uninstall failed'}
'PASS cab experiment defaults off, survives reapply, uninstalls without executable changes.'
