Option Explicit
Dim shell, files, env, scriptPath, ps, command, target
Set shell = CreateObject("WScript.Shell")
Set files = CreateObject("Scripting.FileSystemObject")
If WScript.Arguments.Count > 1 Then
    MsgBox "Drop one executable at a time.", vbInformation, "NEMT"
    WScript.Quit 1
End If
scriptPath = files.BuildPath(files.GetParentFolderName(WScript.ScriptFullName), "NEMT.ps1")
If Not files.FileExists(scriptPath) Then
    MsgBox "Keep this launcher beside NEMT.ps1. Extract the whole ZIP before running it.", vbExclamation, "NEMT"
    WScript.Quit 1
End If
target = ""
If WScript.Arguments.Count = 1 Then target = WScript.Arguments(0)
Set env = shell.Environment("PROCESS")
env("MSTS_DERAIL_SCRIPT") = scriptPath
env("MSTS_DERAIL_TARGET") = target
ps = shell.ExpandEnvironmentStrings("%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe")
' File paths travel as data in this child process environment, never as code.
' This also preserves spaces, apostrophes, &, ! and literal % characters.
command = Chr(34) & ps & Chr(34) & " -NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Hidden -Command " & Chr(34) & "& $env:MSTS_DERAIL_SCRIPT -ExePath $env:MSTS_DERAIL_TARGET" & Chr(34)
On Error Resume Next
shell.Run command, 0, False
If Err.Number <> 0 Then
    MsgBox "Unable to start Windows PowerShell: " & Err.Description, vbExclamation, "NEMT"
    WScript.Quit 1
End If
