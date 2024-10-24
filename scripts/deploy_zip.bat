@echo off

if not "%envvar_set%"=="true" (
    echo "Loading environemnt variables on: setEnvironments.bat"
    call %~dp0/setEnvironments.bat
)

%~d0
cd %~dp0../mappia_publisher/

call pb_tool zip

cd %~dp0