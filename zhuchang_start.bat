@echo off
title Traffic System Launcher - ZhuChang

SET PROJECT_ROOT=%~dp0
IF "%PROJECT_ROOT:~-1%"=="\" SET PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

SET HTTPS_PROXY=
SET HTTP_PROXY=
SET ALL_PROXY=
SET https_proxy=
SET http_proxy=

echo ============================================================
echo  Smart Traffic System Launcher  - ZhuChang
echo ============================================================
echo.

REM --- Read local_config.env ---
IF NOT EXIST "%PROJECT_ROOT%\local_config.env" (
    echo [ERROR] local_config.env not found.
    echo  Create it in the project root and fill in your paths.
    pause
    exit /b 1
)
FOR /F "usebackq eol=# tokens=1,* delims==" %%A IN ("%PROJECT_ROOT%\local_config.env") DO SET %%A=%%B

SET PYSPARK_PYTHON=%PYTHON_EXE%
SET PYSPARK_DRIVER_PYTHON=%PYTHON_EXE%


REM --- Step 1: ZooKeeper ---
echo [1/4] Checking ZooKeeper (port 2181)...
netstat -an | findstr ":2181" | findstr "LISTENING" > nul 2>&1
IF ERRORLEVEL 1 (
    echo       Starting ZooKeeper...
    start "ZooKeeper" cmd /k "%KAFKA_HOME%\bin\windows\zookeeper-server-start.bat %KAFKA_HOME%\config\zookeeper.properties"
    echo       Waiting 8s...
    ping 127.0.0.1 -n 9 > nul
) ELSE (
    echo       ZooKeeper already running. Skip.
)
echo.

REM --- Step 2: Kafka ---
echo [2/4] Checking Kafka (port 9092)...
netstat -an | findstr ":9092" | findstr "LISTENING" > nul 2>&1
IF ERRORLEVEL 1 (
    echo       Waiting 20s for ZooKeeper session expiry...
    ping 127.0.0.1 -n 21 > nul
    echo       Starting Kafka...
    start "Kafka" cmd /k "%KAFKA_HOME%\bin\windows\kafka-server-start.bat %KAFKA_HOME%\config\server.properties"
    echo       Waiting 10s...
    ping 127.0.0.1 -n 11 > nul
) ELSE (
    echo       Kafka already running. Skip.
)
echo.

REM --- MySQL Terminal (optional) ---
IF DEFINED MYSQL_EXE (
    echo [+] Opening MySQL terminal...
    start "MySQL" cmd /k ""%MYSQL_EXE%" -u root -p%MYSQL_PASSWORD% traffic_db"
    echo.
)

REM --- Step 3: Flask ---
echo [3/4] Starting Flask backend...
start "Flask Backend" cmd /k "SET HTTPS_PROXY= && SET HTTP_PROXY= && cd /d %PROJECT_ROOT% && %PYTHON_EXE% flask_backend\app.py"
ping 127.0.0.1 -n 6 > nul
echo       Flask: http://localhost:5000
echo.

REM --- Step 4: Vue ---
echo [4/4] Starting Vue frontend...
start "Vue Frontend" cmd /k "cd /d %PROJECT_ROOT%\web_frontend && npm run dev"
ping 127.0.0.1 -n 6 > nul
echo       Vue:   http://localhost:3000
echo.

echo ============================================================
echo  All services launched!
echo  Frontend : http://localhost:3000
echo  Backend  : http://localhost:5000
echo ============================================================
echo.
echo Press any key to open browser...
pause
start "" "http://localhost:3000"
