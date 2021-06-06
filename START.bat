@echo off

if exist C:\Python39\Lib\site-packages\requests  (python %~dp0\btt-auto-onchain-transfer.py) ^
else (pip install requests && python btt-auto-onchain-transfer.py)
