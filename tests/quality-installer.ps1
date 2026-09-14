param([string]$BaseExe,[string]$WidescreenExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot) 'NEMT.ps1')
foreach($source in @($BaseExe,$WidescreenExe)){foreach($laa in @($false,$true)){
 $dir=[IO.Path]::GetFullPath((Join-Path $Scratch ([Guid]::NewGuid().ToString('N'))));[void][IO.Directory]::CreateDirectory($dir)
 $file=Join-Path $dir 'train.exe';$b=[IO.File]::ReadAllBytes((Resolve-Path $source));if($laa){$b[0x116]=$b[0x116] -bor 0x20};[IO.File]::WriteAllBytes($file,$b);$hash=Get-MstsHash $b
 $wide=(Get-MstsImage $file).Widescreen
 if(-not $wide){
  $rejected=$false;try{Invoke-Options $file $false $false $false -FixCabDials $true -Confirm:$false | Out-Null}catch{$rejected=$_.Exception.Message -like '*requires*'}
  if(-not $rejected -or (Test-Path (Join-Path $dir 'DINPUT.dll'))){throw 'Non-widescreen cab option was not rejected cleanly'}
 }
 foreach($bits in 1..7){
  $cab=$wide -and (($bits -band 1) -ne 0);$audio=($bits -band 2) -ne 0;$red=($bits -band 4) -ne 0
  if(-not ($cab -or $audio -or $red)){continue}
  Invoke-Options $file $false $false $false -FixCabDials $cab -BackgroundAudio $audio -IgnoreRedSignal $red -Confirm:$false | Out-Null
  $text=[IO.File]::ReadAllText((Join-Path $dir 'NEMT/settings.ini'))
  foreach($pair in @(@('CorrectNeedleAspect',$cab),@('UnmuteInBackground',$audio),@('IgnoreRedSignal',$red))){if(-not $text.Contains($pair[0]+'='+$pair[1].ToString().ToLowerInvariant())){throw 'New setting mismatch'}}
 }
 Invoke-Options $file $false $false $false -FixCabDials $false -Confirm:$false | Out-Null
 if(Test-Path (Join-Path $dir 'DINPUT.dll')){throw 'Uninstall failed'}
 if((Get-MstsHash ([IO.File]::ReadAllBytes($file))) -ne $hash){throw 'Executable modified'}
}}
'PASS quality options across four variants: widescreen gating, independent installs, settings persistence and uninstall; EXE unchanged.'
