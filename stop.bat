@echo off
echo Stopping Google Places Scraper...
taskkill /F /FI "WINDOWTITLE eq Backend*" /IM python.exe 2>nul
taskkill /F /FI "WINDOWTITLE eq Frontend*" /IM cmd.exe 2>nul
taskkill /F /FI "WINDOWTITLE eq Frontend*" /IM node.exe 2>nul
echo Done.
pause
