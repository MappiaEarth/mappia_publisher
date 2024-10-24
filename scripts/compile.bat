if not "%envvar_set%"=="true" (
    echo "Loading environemnt variables on: setEnvironments.bat"
    call %~dp0/setEnvironments.bat
)

%~d0
cd %~dp0../src/

@echo on
pyrcc5 -o resources.py resources.qrc