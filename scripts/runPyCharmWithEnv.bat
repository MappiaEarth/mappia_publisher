if not "%envvar_set%"=="true" (
    echo "Loading environemnt variables on: setEnvironments.bat"
    call %~dp0/setEnvironments.bat
)

"%IDE_PATH%"
