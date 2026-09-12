param([string]$BaseExe,[string]$WidescreenExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot) 'NEMT.ps1')
foreach($source in @($BaseExe,$WidescreenExe)){foreach($laa in @($false,$true)){
 $dir=[IO.Path]::GetFullPath((Join-Path $Scratch ([Guid]::NewGuid().ToString('N'))));[void][IO.Directory]::CreateDirectory($dir)
 $file=Join-Path $dir 'train.exe';$b=[IO.File]::ReadAllBytes((Resolve-Path $source));if($laa){$b[0x116]=$b[0x116] -bor 0x20}else{$b[0x116]=$b[0x116] -band 0xdf};[IO.File]::WriteAllBytes($file,$b);$hash=Get-MstsHash $b
 foreach($bits in 1..15){
  $v=($bits -band 1) -ne 0;$l=($bits -band 2) -ne 0;$fps=($bits -band 4) -ne 0;$hud=($bits -band 8) -ne 0
  Invoke-Options $file $false $false $false -VerboseLoading $v -StartupLog $l -UnlockFPS $fps -CrawlHUD $hud -Confirm:$false | Out-Null
  $m=Get-CrawlInstallation $file
  if($m.verboseLoading -ne $v -or $m.startupLog -ne $l -or $m.unlockFPS -ne $fps -or $m.crawlHUD -ne $hud){throw 'Startup flags mismatch'}
  $ini=[IO.File]::ReadAllText((Join-Path $dir 'NEMT/native.ini'))
  foreach($pair in @(@('VerboseLoading',$v),@('WriteLog',$l),@('UnlockFPS',$fps),@('ShowCrawlHUD',$hud))){if(-not $ini.Contains(($pair[0]+'='+$pair[1].ToString().ToLowerInvariant()))){throw 'INI mismatch'}}
  if(Test-Path (Join-Path $dir 'NEMT/startup.log')){throw 'Installer should not write startup log'}
 }
 Invoke-Options $file $false $false $false -Confirm:$false | Out-Null
 if(Test-Path (Join-Path $dir 'DINPUT.dll')){throw 'Uninstall failed'}
 if((Get-MstsHash ([IO.File]::ReadAllBytes($file))) -ne $hash){throw 'Executable changed'}
}}
'PASS 60 startup/HUD feature combinations across four variants, opt-in settings, no installer log writes and unchanged EXE.'
