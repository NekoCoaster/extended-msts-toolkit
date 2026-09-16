param([string]$BaseExe,[string]$WidescreenExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Join-Path (Split-Path $PSScriptRoot) 'legacy') 'NEMT.ps1')
foreach($source in @($BaseExe,$WidescreenExe)){
 $dir=Join-Path $Scratch ([guid]::NewGuid().ToString('N'));[void][IO.Directory]::CreateDirectory($dir)
 $file=Join-Path $dir 'train.exe';[IO.File]::WriteAllBytes($file,[IO.File]::ReadAllBytes((Resolve-Path $source)))
 $before=Get-MstsHash ([IO.File]::ReadAllBytes($file))
 Invoke-Options $file $true $true $true 10 -Confirm:$false | Out-Null
 $ini=Join-Path $dir 'NEMT/settings.ini';$text=[IO.File]::ReadAllText($ini)
 if(-not $text.Contains('DerailKey=BACKSLASH')){throw 'Missing default derail key'}
 foreach($key in @('F12','NONE')){
  $text=[IO.File]::ReadAllText($ini) -replace '(?m)^DerailKey=[^\r\n]*',('DerailKey='+$key)
  [IO.File]::WriteAllText($ini,$text)
  Invoke-Options $file $true $true $true 10 -Confirm:$false | Out-Null
  if(-not ([IO.File]::ReadAllText($ini)).Contains('DerailKey='+$key)){throw 'Custom key lost on Apply'}
 }
 if((Get-MstsHash ([IO.File]::ReadAllBytes($file))) -ne $before){throw 'Executable changed'}
}
'PASS base/widescreen default derail key, custom/disabled key persistence and unchanged EXE.'
