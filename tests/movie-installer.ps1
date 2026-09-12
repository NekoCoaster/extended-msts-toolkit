param([string]$BaseExe,[string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot) 'NEMT.ps1')
$dir=[IO.Path]::GetFullPath((Join-Path $Scratch ([Guid]::NewGuid().ToString('N'))));[void][IO.Directory]::CreateDirectory($dir)
$file=Join-Path $dir 'train.exe';Copy-Item -LiteralPath $BaseExe -Destination $file
Invoke-Options $file $false $false $false -WindowFeatures $true -Confirm:$false | Out-Null
$ini=Join-Path $dir 'NEMT/settings.ini';$text=[IO.File]::ReadAllText($ini)
foreach($key in @('BindMovieOutput','UseSystemMovieDecoder','RestoreMovieFocus','SeparateMovieWindow')){if(-not $text.Contains("$key=true")){throw 'Missing default movie fix'}}
$text=$text.Replace('BindMovieOutput=true','BindMovieOutput=false').Replace('SeparateMovieWindow=true','SeparateMovieWindow=false').Replace('UseSystemMovieDecoder=true','UseSystemMovieDecoder=false').Replace('RestoreMovieFocus=true','RestoreMovieFocus=false');[IO.File]::WriteAllText($ini,$text)
Invoke-Options $file $false $false $false -WindowFeatures $true -Confirm:$false | Out-Null
$text=[IO.File]::ReadAllText($ini)
foreach($key in @('BindMovieOutput','UseSystemMovieDecoder','RestoreMovieFocus','SeparateMovieWindow')){if(-not $text.Contains("$key=false")){throw 'Movie comparison setting lost'}}
'PASS movie fixes enabled on apply; explicit comparison switches preserved.'
