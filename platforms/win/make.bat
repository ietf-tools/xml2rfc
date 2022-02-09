@ECHO OFF
set GUI_PATH=..\..\..\gui
set CLI_PATH=..\..\..\cli
set BUILDROOT=build

echo Preparing build directory...
mkdir dist
mkdir "%BUILDROOT%"
mkdir "%BUILDROOT%\xml2rfc"
mkdir "%BUILDROOT%\xml2rfc_gui"
mkdir "%BUILDROOT%\assets"
xcopy /E /Y /EXCLUDE:exclude.txt "%GUI_PATH%\xml2rfc_gui" "%BUILDROOT%\xml2rfc_gui"
xcopy /E /Y /EXCLUDE:exclude.txt "%GUI_PATH%\assets" "%BUILDROOT%\assets"
xcopy /E /Y /EXCLUDE:exclude.txt "%CLI_PATH%\xml2rfc" "%BUILDROOT%\xml2rfc"
copy scripts\setup.spec "%BUILDROOT%"
copy ..\..\shared\xml2rfc-gui.py "%BUILDROOT%"

echo Configuring pyinstaller...
python pyinstaller\Configure.py

echo Building with pyinstaller...
cd "%BUILDROOT%"
python ..\pyinstaller\Build.py setup.spec
copy assets\xml2rfc.ico dist\xml2rfc-gui

cd ..
echo Finished building, output in %BUILDROOT%\dist.  Please run vs2008\setup\setup.vdproj to build MSI.
pause