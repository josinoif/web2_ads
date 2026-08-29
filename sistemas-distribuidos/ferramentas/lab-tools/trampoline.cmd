@echo off
REM Encaminha para lab.ps1 desta pasta (que sobe até sistemas-distribuidos/lab.ps1).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0lab.ps1" %*
