rem set OSGEO=C:\OSGeo4W64
rem set PATH=%OSGEO%\apps\Python37\Scripts\;%OSGEO%\bin\python3.exe;%PATH%
rem SET OSGEO4W_ROOT=%OSGEO%
rem call "%OSGEO4W_ROOT%"\bin\o4w_env.bat
rem call "%OSGEO4W_ROOT%"\apps\grass\grass78\etc\env.bat
rem
rem path %PATH%;%OSGEO4W_ROOT%\apps\qgis\bin
rem path %PATH%;%OSGEO4W_ROOT%\apps\grass\grass78\lib
rem path %PATH%;%OSGEO%\apps\Qt5\bin
rem path %PATH%;%OSGEO%\apps\Python37\Scripts
rem
rem set PYTHONPATH=C:\python38\Scripts\;C:\python38\;E:\Danilo\Programas\Dinamica EGO 5\PyEnvironment\
rem set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis\python
rem set PYTHONHOME=%OSGEO4W_ROOT%\apps\Python37
rem
rem set PATH=E:\Danilo\Programas\GitPortable\App\Git\bin\;%PATH%
rem path %OSGEO4W_ROOT%\apps\qgis\bin;%PATH%
rem set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis
rem set GDAL_FILENAME_IS_UTF8=YES
rem set VSI_CACHE=TRUE
rem set VSI_CACHE_SIZE=1000000
rem set QT_PLUGIN_PATH=%OSGEO4W_ROOT%\apps\qgis\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
rem set QGIS_PLUGINPATH=%OSGEO4W_ROOT%\apps\qgis\qtplugins;%OSGEO4W_ROOT%\apps\qt5\plugins
rem rem easy_install pb_tool
rem rem python -m pip install pb_tool

if not "%envvar_set%"=="true" (
    echo "Loading environemnt variables on: setEnvironments.bat"
    call %~dp0/setEnvironments.bat
)

%~d0
cd %~dp0../mappia_publisher/

call pb_tool deploy -y

cd %~dp0