@echo off
chcp 65001 >nul
cd /d "%~dp0"
rem Nuitka 的编译缓存/工具链（数百 MB~数 GB）默认在 C:\Users\...\AppData\Local\Nuitka。
rem 想换到本目录（或其它盘）时取消下面一行注释——C 盘紧张时很有用：
rem set "NUITKA_CACHE_DIR=%~dp0.nuitka-cache"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" build.py %*
) else (
    python build.py %*
)
echo.
pause
