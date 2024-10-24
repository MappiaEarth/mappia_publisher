if not "%envvar_set%"=="true" (
    echo "Loading environemnt variables on: setEnvironments.bat"
    call %~dp0/setEnvironments.bat
)

pyuic5 ../mappia_publisher/share_maps.ui -o ../mappia_publisher/share_maps.py
