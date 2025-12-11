@echo off
echo Installing dependencies...
call npm install
echo Building project...
call npm run build
echo Build complete!
pause
