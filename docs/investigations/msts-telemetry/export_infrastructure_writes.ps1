param([Parameter(Mandatory=$true)][string]$Pass,[Parameter(Mandatory=$true)][string[]]$Addresses)
$ErrorActionPreference='Stop'
$toolRoot='C:\codex\reference\historical-tasks\2026-09-05\referenced-chatgpt-conversation-this-is-an\work\tools'
$env:JAVA_HOME=Join-Path $toolRoot 'jdk-21.0.12.1+1'
$env:JAVA_TOOL_OPTIONS='-Duser.name=NekoCoaster -Duser.home=C:/dev/Codex/2026-09-10/msts-telemetry/ghidra-home'
$env:APPDATA=Join-Path $PSScriptRoot 'ghidra-home\Roaming'
$env:LOCALAPPDATA=Join-Path $PSScriptRoot 'ghidra-home\Local'
New-Item -ItemType Directory -Path $env:APPDATA,$env:LOCALAPPDATA -Force | Out-Null
$output=Join-Path $PSScriptRoot $Pass
New-Item -ItemType Directory -Path $output -Force | Out-Null
$exportArgs=@('C:\dev\Codex\2026-09-10\msts-precipitation\ghidra-projects','MSTS','-process','train.exe','-noanalysis','-readOnly','-scriptPath',$PSScriptRoot,'-postScript','TelemetryInfrastructureWrites.java',$output)
$exportArgs+=$Addresses
$exportArgs+=@('-max-cpu','2','-log',(Join-Path $output 'ghidra.log'),'-scriptlog',(Join-Path $output 'script.log'))
& (Join-Path $toolRoot 'ghidra_12.1.3_PUBLIC\support\analyzeHeadless.bat') @exportArgs *> (Join-Path $output 'console.log')
Get-Content (Join-Path $output 'console.log') -Tail 15
if(-not(Test-Path (Join-Path $output 'writes.tsv'))) {throw 'Export missing; inspect console.log'}
