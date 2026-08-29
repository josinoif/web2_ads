@echo off
REM Atalho cmd.exe → lab.ps1 (na pasta do lab use o lab.cmd de lá, ou este na raiz).
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0lab.ps1" %*
