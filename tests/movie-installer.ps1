param([string]$BaseExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot) 'NEMT.ps1')
$dir=[IO.Path]::GetFullPath((Join-Path $Scratch ([Guid]::NewGuid().ToString('N'))));[void][IO.Directory]::CreateDirectory($dir)
$file=Join-Path $dir 'train.exe';Copy-Item -LiteralPath $BaseExe -Destination $file
$hash=(Get-FileHash -LiteralPath $file).Hash
foreach($skip in @($false,$true)){
 Invoke-Options $file $false $false $false -WindowFeatures $true -SkipStartupMovie $skip -Confirm:$false | Out-Null
 $ini=Join-Path $dir 'NEMT/settings.ini';$text=[IO.File]::ReadAllText($ini)
 if(-not $text.Contains("SkipStartupMovie=$($skip.ToString().ToLowerInvariant())") -or -not $text.Contains("RestoreMovieFocus=$($skip.ToString().ToLowerInvariant())")){throw 'Movie checkbox value mismatch'}
 if($text -match 'SeparateMovieWindow|UseSystemMovieDecoder|BindMovieOutput'){throw 'Experimental renderer option retained'}
 if((Get-FileHash -LiteralPath $file).Hash -ne $hash){throw 'Executable changed'}
}
Invoke-Options $file $false $false $false -SkipStartupMovie $true -Confirm:$false | Out-Null
if(-not (Test-Path -LiteralPath (Join-Path $dir 'DINPUT.dll'))){throw 'Skip-only installation failed'}
Invoke-Options $file $false $false $false -Confirm:$false | Out-Null
if(Test-Path -LiteralPath (Join-Path $dir 'DINPUT.dll')){throw 'Uninstall failed'}
if((Get-FileHash -LiteralPath $file).Hash -ne $hash){throw 'Executable changed during uninstall'}
'PASS combined movie option states, native-rendering config, skip-only installation, uninstall and unchanged executable.'
