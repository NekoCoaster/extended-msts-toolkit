param([Parameter(Mandatory=$true)][string]$BaseExe,[Parameter(Mandatory=$true)][string]$Scratch)
$ErrorActionPreference='Stop'
. (Join-Path (Split-Path $PSScriptRoot) 'NEMT.ps1')
function Assert($c,$m){if(-not $c){throw $m}}
# Substitute registry results, without creating or changing registry entries.
$script:RegistryTestValues=@();$script:RegistryReads=0
function Get-MstsRegistryPaths {$script:RegistryReads++;$script:RegistryTestValues}
$dir=[IO.Path]::GetFullPath((Join-Path $Scratch ([Guid]::NewGuid().ToString('N'))));[void][IO.Directory]::CreateDirectory($dir)
$validDir=Join-Path $dir "MSTS user's install";[void][IO.Directory]::CreateDirectory($validDir)
$valid=Join-Path $validDir 'train.exe';[IO.File]::Copy((Resolve-Path $BaseExe).Path,$valid)
$invalidDir=Join-Path $dir 'unsupported';[void][IO.Directory]::CreateDirectory($invalidDir)
$invalid=Join-Path $invalidDir 'train.exe';[IO.File]::WriteAllText($invalid,'unsupported fixture')
$valid=[IO.Path]::GetFullPath($valid);$invalid=[IO.Path]::GetFullPath($invalid)
$script:RegistryTestValues=@($validDir)
Assert ((Resolve-MstsStartupPath 'explicit-file.exe') -eq 'explicit-file.exe') 'Explicit path was replaced'
Assert ($script:RegistryReads -eq 0) 'Explicit path must bypass registry reads'
Assert ((Resolve-MstsStartupPath '') -eq $valid) 'Installation directory not resolved'
$script:RegistryTestValues=@('"'+$valid+'"')
Assert ((Resolve-MstsStartupPath '') -eq $valid) 'Quoted executable path not resolved'
$env:MEDS_DISCOVERY_TEST_ROOT=[IO.Path]::GetDirectoryName($valid)
try{
 $script:RegistryTestValues=@('%MEDS_DISCOVERY_TEST_ROOT%')
 Assert ((Resolve-MstsStartupPath '') -eq $valid) 'Environment expansion failed'
}finally{Remove-Item Env:MEDS_DISCOVERY_TEST_ROOT}
$script:RegistryTestValues=@('relative-path',(Join-Path $dir 'missing'),$invalidDir,$validDir)
Assert ((Resolve-MstsStartupPath '') -eq $valid) 'Supported candidate should beat stale or unsupported entries'
$script:RegistryTestValues=@($invalidDir)
Assert ((Resolve-MstsStartupPath '') -eq $invalid) 'Unsupported installed executable must be available for normal validation feedback'
$script:RegistryTestValues=@('relative-path',(Join-Path $dir 'missing'))
Assert ([string]::IsNullOrEmpty((Resolve-MstsStartupPath ''))) 'Missing installations should leave Browse available'
$script:RegistryTestValues=@()
Assert ([string]::IsNullOrEmpty((Resolve-MstsStartupPath ' '))) 'Empty registry should leave path empty'
Write-Output 'PASS startup discovery: explicit-path priority, directory, quoted executable, environment expansion, stale/unsupported fallback and absent registry. No registry writes.'
