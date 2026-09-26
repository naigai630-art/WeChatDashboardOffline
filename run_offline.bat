@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
title 微信聊天量化看板 离线版
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"

echo [信息] 项目目录：%CD%

if not exist "offline\runtime\python\python.exe" (
  echo [错误] 缺少离线 Python 运行环境。
  echo 请使用 QuantifyingWeChatChatRecords-Offline-Windows-x64.zip 完整包。
  pause
  exit /b 1
)

if not exist "tools\offline_launcher.py" (
  echo [错误] 缺少 tools\offline_launcher.py。
  echo 请完整解压 ZIP，不要在压缩包预览窗口内运行。
  pause
  exit /b 1
)

"offline\runtime\python\python.exe" "tools\offline_launcher.py"
set "RUN_RESULT=%ERRORLEVEL%"

echo.
if "%RUN_RESULT%"=="0" (
  echo [完成] 程序已正常结束，退出代码：0
) else (
  echo [失败] 程序退出代码：%RUN_RESULT%
  echo 请将本窗口中的完整报错截图发回。
)

echo.
pause
endlocal
exit /b %RUN_RESULT%
