@ECHO off
SETLOCAL ENABLEDELAYEDEXPANSION
SET count=1
FOR /F "tokens=* USEBACKQ" %%F IN (`py -m pip show requests`) DO (
  SET var!count!=%%F
  SET /a count=!count!+1
)
set b=Name: requests
if !var1! == !b! (ECHO requests module is already installed) ^
else (py -m pip install requests)
SET count=1
FOR /F "tokens=* USEBACKQ" %%F IN (`py -m pip show pyTelegramBotAPI`) DO (
  SET var!count!=%%F
  SET /a count=!count!+1
)
set b=Name: pyTelegramBotAPI
if !var1! == !b! (ECHO pyTelegramBotAPI module is already installed) ^
else (py -m pip install pyTelegramBotAPI)
if exist %~dp0\btt-auto-onchain-transfer.py  (py %~dp0\btt-auto-onchain-transfer.py) ^
else (ECHO Script file not found)
ENDLOCAL
