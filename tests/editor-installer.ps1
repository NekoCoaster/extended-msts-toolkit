param([string]$BaseExe,[string]$WidescreenExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot) 'NEMT.ps1')
foreach($source in @($BaseExe,$WidescreenExe)){foreach($laa in @($false,$true)){
 $dir=[IO.Path]::GetFullPath((Join-Path $Scratch ([Guid]::NewGuid().ToString('N'))));[void][IO.Directory]::CreateDirectory($dir)
 $file=Join-Path $dir 'train.exe';$b=[IO.File]::ReadAllBytes((Resolve-Path $source));if($laa){$b[0x116]=$b[0x116] -bor 0x20};[IO.File]::WriteAllBytes($file,$b);$hash=Get-MstsHash $b
 foreach($bits in 1..15){
  $windows=($bits -band 1) -ne 0;$tools=($bits -band 2) -ne 0;$audio=($bits -band 4) -ne 0
  $keys=($bits -band 8) -ne 0
  Invoke-Options $file $false $false $false -FixCabDials $false -EditorWindows $windows -FreeEditorTools $tools -SmoothEditorAudio $audio -SwapEditorKeys $keys -Confirm:$false | Out-Null
  $text=[IO.File]::ReadAllText((Join-Path $dir 'NEMT/settings.ini'))
  $manifest=Get-Content (Join-Path $dir 'NEMT/installation.json') -Raw | ConvertFrom-Json
  foreach($pair in @(@('ResizableViewports',$windows),@('FreeToolWindows',$tools),@('SmoothIdleAudio',$audio),@('SwapArrowKeys',$keys))){if(-not $text.Contains($pair[0]+'='+$pair[1].ToString().ToLowerInvariant())){throw 'Editor setting mismatch'}}
  if($manifest.editorWindows -ne $windows -or $manifest.freeEditorTools -ne $tools -or $manifest.smoothEditorAudio -ne $audio -or $manifest.swapEditorKeys -ne $keys){throw 'Editor manifest mismatch'}
  if($bits -eq 1){[IO.File]::WriteAllText((Join-Path $dir 'NEMT/settings.ini'),$text.Replace('RE_CAM_FORWARD=w','RE_CAM_FORWARD=i'))}
  elseif(-not $text.Contains('RE_CAM_FORWARD=i')){throw 'Custom camera binding lost on Apply'}
 }
 Invoke-Options $file $false $false $false -FixCabDials $false -Confirm:$false | Out-Null
 if(Test-Path (Join-Path $dir 'DINPUT.dll')){throw 'Uninstall failed'}
 if((Get-MstsHash ([IO.File]::ReadAllBytes($file))) -ne $hash){throw 'Executable modified'}
}}
'PASS editor options: all sixteen combinations across four executable variants, independent installation, custom binding persistence and uninstall; EXE unchanged.'
