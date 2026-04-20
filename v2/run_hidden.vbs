'' Launches KARE server with no visible console window.
'' Used by install_service.bat (Task Scheduler). Can also be double-clicked.
Dim dir, cmd
dir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
cmd = "python """ & dir & "server.py"""
CreateObject("WScript.Shell").Run cmd, 0, False
