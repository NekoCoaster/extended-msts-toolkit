param([string]$BaseExe,[string]$WidescreenExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Join-Path (Split-Path $PSScriptRoot) 'legacy') 'NEMT.ps1')
foreach($source in @($BaseExe,$WidescreenExe)){foreach($laa in @($false,$true)){
 $dir=[IO.Path]::GetFullPath((Join-Path $Scratch ([Guid]::NewGuid().ToString('N'))));[void][IO.Directory]::CreateDirectory($dir)
 $file=Join-Path $dir 'train.exe';$bytes=[IO.File]::ReadAllBytes((Resolve-Path $source));if($laa){$bytes[0x116]=$bytes[0x116] -bor 0x20}else{$bytes[0x116]=$bytes[0x116] -band 0xdf}
 [IO.File]::WriteAllBytes($file,$bytes);$hash=Get-MstsHash $bytes
 Invoke-Options $file $false $false $false -WindowFeatures $true -Confirm:$false | Out-Null
 $manifest=Get-CrawlInstallation $file
 if(-not $manifest.windowFeatures -or $manifest.crawl -or $manifest.preventEnd -or $manifest.unlockCameras){throw 'Window-only flags mismatch'}
 $ini=Join-Path $dir 'NEMT/settings.ini';$text=[IO.File]::ReadAllText($ini)
 if($text -notmatch '\[Window\]\s+Enabled=true\s+CenterWindowed=true'){throw 'Window configuration missing'}
 [IO.File]::WriteAllText($ini,$text.Replace('CenterWindowed=true','CenterWindowed=false'))
 Invoke-Options $file $true $true $true -WindowFeatures $true -Confirm:$false | Out-Null
 if([IO.File]::ReadAllText($ini) -notmatch 'CenterWindowed=false'){throw 'Centering preference lost'}
 if((Get-MstsHash ([IO.File]::ReadAllBytes($file))) -ne $hash){throw 'Executable changed'}
 Invoke-Options $file $false $false $false -Confirm:$false | Out-Null
 if(Test-Path (Join-Path $dir 'DINPUT.dll')){throw 'Uninstall left window DLL'}
}}
'PASS window-only install, combined features, preserved centering preference, unchanged EXE and uninstall for all four variants.'
