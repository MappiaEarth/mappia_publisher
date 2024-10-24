@echo off

echo Setting environment Variables:

rem FILE PATH to QGIS with GRASS to "o4w_env.bat"
rem set OSGEO=C:\OSGeo4W64
set OSGEO=C:\Program Files\QGIS 3.14
set GIT_BIN=C:\Danilo\Programas\PortableGit\bin\
set GRASS_BASEPATH=%OSGEO%\apps\grass\grass*
set PYTHONHOME=%OSGEO%\apps\Python*
set QT_BIN=%OSGEO%\apps\Qt*
set IDE_PATH=C:\Program Files\JetBrains\PyCharm 2023.2.5\bin\pycharm64.exe

call :setMatchingPath "%GRASS_BASEPATH%" "GRASS_BASEPATH"
call :setMatchingPath "%PYTHONHOME%" "PYTHONHOME"
call :setMatchingPath "%QT_BIN%" "QT_BIN"

set PYTHON_VER_FOLDER=_holder_
call :getLastPath "%PYTHONHOME%" "PYTHON_VER_FOLDER"

set OSGEO4W_ROOT=%OSGEO%

call "%OSGEO%\bin\o4w_env.bat"
call "%OSGEO%\bin\qt5_env.bat"
call "%OSGEO%\bin\py3_env.bat"
call "%GRASS_BASEPATH%\etc\env.bat"

set QGIS_PYTHON=%APPDATA%\Python\%PYTHON_VER_FOLDER%
set PATH=%QGIS_PYTHON%\Scripts;%OSGEO%\apps\qgis\bin;%PYTHONHOME%\Scripts\;%QT_BIN%;%GIT_BIN%;%PYTHONHOME%\Scripts\;%PYTHONHOME%\DLLs\;%OSGEO4W_ROOT%\apps\qgis\bin;%GRASS_BASEPATH%\lib;%PATH%
echo PythonFolder: %PYTHON_VER_FOLDER% fullPath: %QGIS_PYTHON%

set PYTHONPATH=%PYTHONPATH%;%OSGEO%\apps\qgis\python
set QGIS_PREFIX_PATH=%OSGEO4W_ROOT:\=/%/apps/qgis
set GDAL_FILENAME_IS_UTF8=YES
set VSI_CACHE=TRUE
set VSI_CACHE_SIZE=1000000
set QT_PLUGIN_PATH=%OSGEO%\apps\qgis\qtplugins;%QT_BIN%\plugins
set QGIS_PLUGINPATH=%OSGEO%\apps\qgis\qtplugins;%QT_BIN%\plugins
rem set PATH=%PYTHONPATH%;%PATH%
rem easy_install pb_tool
rem python -m pip install pb_tool

python -m pip install pickled
python -m pip install pyproj
python -m pip install pb_tool
rem If fail to install pb_tool, try to use: easy_install pb_tool

rem if not "%envvar_set%"=="true" (
rem     echo Setting environment path variable
rem     SET "PATH=%JAVA_HOME%;%JAVA_EXE%;%ANT_DIR%;%NODEJS_HOME%;%PATH%"
rem ) else (
rem     echo "Environment variable already set, use 'set envvar_set=false', to allow script rewrite the Environment variable 'PATH' ."
rem )
rem
set envvar_set=true


rem Rest of the script, functions
goto :eof

:getLastPath
set "fromPath=%~1"
set "varName=%~2"
for %%F in ("%fromPath%") do set "lastPath=%%~nxF"
set "%varName%=%lastPath%"
echo LastPath from '%fromPath%' assigning to %varName% returns '%lastPath%'
goto :endFunction

rem Function-like label to find the grass path
:setMatchingPath
set "searchPath=%~1"
set "varName=%~2"

rem for /d %%G in ("%searchPath%\%startingWith%*") do (
for /d %%G in ("%searchPath%") do (
    set "%varName%=%%G"
    echo MatchingPath: Variable '%varName%' = '%%G'
    goto :endFunction
)
echo Failed to find matching path on %searchPath% , variable %varName% was not updated.
pause

:endFunction
exit /b
