param([string]$BaseExe,[string]$WidescreenExe,[string]$Scratch,[string[]]$LegacyPatchers)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot) 'NEMT.ps1')
function Assert($c,$m){if(-not $c){throw $m}}
$count=0
foreach($wide in @($false,$true)){foreach($laa in @($false,$true)){
 $dir=[IO.Path]::GetFullPath((Join-Path $Scratch ([Guid]::NewGuid().ToString('N'))));[void][IO.Directory]::CreateDirectory($dir)
 $file=Join-Path $dir 'train.exe';$fixture=if($wide){$WidescreenExe}else{$BaseExe};$b=[IO.File]::ReadAllBytes((Resolve-Path $fixture))
 Set-PatchBytes $b $script:Specs.Timeout $false;Set-PatchBytes $b $script:Specs.Camera $false
 if($laa){$b[0x116]=$b[0x116] -bor 0x20}else{$b[0x116]=$b[0x116] -band 0xdf};[IO.File]::WriteAllBytes($file,$b);$hash=Get-MstsHash $b
 [IO.File]::WriteAllText((Join-Path $dir 'DDraw.dll'),'unrelated graphics wrapper')
 foreach($bits in 0..7){
  $t=($bits -band 1) -ne 0;$c=($bits -band 2) -ne 0;$crawl=($bits -band 4) -ne 0;$rejected=$false
  try{Invoke-Options $file $t $c $crawl 10 -Confirm:$false | Out-Null}catch{if($crawl -and -not $t){$rejected=$true}else{throw}}
  Assert ($rejected -eq ($crawl -and -not $t)) 'Dependency validation mismatch'
  Assert ((Get-MstsHash ([IO.File]::ReadAllBytes($file))) -eq $hash) 'Clean executable was written'
  if(-not $rejected -and $bits){$m=Get-CrawlInstallation $file;Assert ($m.preventEnd -eq $t -and $m.unlockCameras -eq $c -and $m.crawl -eq $crawl) 'Saved feature flags mismatch';Assert ($m.crawlHUD -eq $crawl) 'HUD must follow crawl selection'}
  $count++
 }
 Invoke-Options $file $false $false $false -Confirm:$false | Out-Null
 Assert (-not (Test-Path (Join-Path $dir 'DINPUT.dll'))) 'Uninstall left DLL'
 Assert ([IO.File]::ReadAllText((Join-Path $dir 'DDraw.dll')) -eq 'unrelated graphics wrapper') 'Graphics wrapper changed'
 Assert (@(Get-ChildItem $dir -Filter '*.bak').Count -eq 0) 'Clean install should not create an executable backup'
 Invoke-Options $file $true $true $true -WhatIf | Out-Null
 Assert (-not (Test-Path (Join-Path $dir 'DINPUT.dll'))) 'Dry run installed files'
 [IO.File]::WriteAllText((Join-Path $dir 'DINPUT.dll'),'unrelated input wrapper')
 $rejected=$false;try{Invoke-Options $file $true $false $false -Confirm:$false | Out-Null}catch{$rejected=$true}
 Assert $rejected 'Unrelated input wrapper accepted'
 Assert ([IO.File]::ReadAllText((Join-Path $dir 'DINPUT.dll')) -eq 'unrelated input wrapper') 'Unrelated input wrapper overwritten'
}}
foreach($legacy in $LegacyPatchers){
 $dir=[IO.Path]::GetFullPath((Join-Path $Scratch ([Guid]::NewGuid().ToString('N'))));[void][IO.Directory]::CreateDirectory($dir);$file=Join-Path $dir 'train.exe';[IO.File]::Copy((Resolve-Path $BaseExe),$file)
 & $legacy -Action Apply -ExePath $file -RemoveEndMessage -UnlockCameras -Crawl | Out-Null
 $patchedHash=(Get-MstsImage $file).SHA256
 Invoke-Options $file $true $true $true 10 -Confirm:$false | Out-Null
 $i=Get-MstsImage $file;Assert (-not $i.TimeoutPatched -and -not $i.CameraPatched) 'Legacy bytes were not restored'
 $backup=$file+'.nemt-migration.'+$patchedHash.Substring(0,16)+'.bak';Assert ((Get-MstsHash ([IO.File]::ReadAllBytes($backup))) -eq $patchedHash) 'Migration backup mismatch'
 Assert ((Get-CrawlInstallation $file).product -eq 'NEMT') 'Toolkit ownership not established'
 foreach($folder in @('MEDS','MSTS-Derailment')){foreach($name in @('native.ini','MstsCrawl.dll','crawl.js','MstsCrawl.config')){Assert (-not (Test-Path (Join-Path $dir "$folder/$name"))) 'Active legacy payload remains'}}
 $cleanHash=$i.SHA256;Invoke-Options $file $false $true $false 0 -Confirm:$false | Out-Null
 Assert ((Get-MstsImage $file).SHA256 -eq $cleanHash) 'Changing settings rewrote executable'
 Invoke-Options $file $false $false $false -Confirm:$false | Out-Null
 Assert ((Get-MstsImage $file).SHA256 -eq $cleanHash) 'Uninstall rewrote clean executable'
}
Write-Output "PASS $count feature/variant cases; clean EXE invariant; migration from $($LegacyPatchers.Count) releases; backup, settings, uninstall, dry-run and wrapper preservation."
