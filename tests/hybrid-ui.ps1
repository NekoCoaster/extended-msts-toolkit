$ErrorActionPreference='Stop'
. (Join-Path (Join-Path (Split-Path $PSScriptRoot) 'legacy') 'NEMT.ps1')
$detected=Test-HybridCpuSupport
$data=New-Object byte[] 64
[BitConverter]::GetBytes([uint32]32).CopyTo($data,0)
[BitConverter]::GetBytes([uint32]32).CopyTo($data,32)
$data[46]=1
if([NemtCpuTopology]::HasSupportedClasses($data)){throw 'Homogeneous CPU enabled'}
$data[50]=1
if(-not [NemtCpuTopology]::HasSupportedClasses($data)){throw 'Hybrid CPU disabled'}
$data[44]=1
if([NemtCpuTopology]::HasSupportedClasses($data)){throw 'Unsupported group enabled'}
$data[44]=0;$data[46]=32
if([NemtCpuTopology]::HasSupportedClasses($data)){throw 'Unsupported logical index enabled'}
$data[46]=1;$data[32]=0
if([NemtCpuTopology]::HasSupportedClasses($data)){throw 'Malformed topology enabled'}
if([NemtCpuTopology]::HasSupportedClasses((New-Object byte[] 0))){throw 'Empty topology enabled'}
"PASS homogeneous, hybrid, unsupported group/index, malformed and empty detection; host support=$detected."
