rmdir /S /Q ..\build\Lunatranslator 
xcopy ..\build\x64\LunaTranslator_main.dist ..\build\LunaTranslator\LunaTranslator /e /y /I
xcopy .\files ..\build\LunaTranslator\files /e /y /I
copy ..\LICENSE ..\build\LunaTranslator\
xcopy .\LunaTranslator\ocrengines ..\build\LunaTranslator\LunaTranslator\ocrengines /e /y /I
xcopy .\LunaTranslator\postprocess ..\build\LunaTranslator\LunaTranslator\postprocess /e /y /I
xcopy .\LunaTranslator\translator ..\build\LunaTranslator\LunaTranslator\translator /e /y /I
xcopy .\LunaTranslator\cishu ..\build\LunaTranslator\LunaTranslator\cishu /e /y /I
xcopy ..\dependence\dependence_common ..\build\LunaTranslator\LunaTranslator /e /y /I 
xcopy ..\dependence\dependence64 ..\build\LunaTranslator\LunaTranslator /e /y /I 
xcopy ..\dependence\api-ms-win_64 ..\build\LunaTranslator\LunaTranslator /e /y /I
xcopy ..\dependence\exe64 ..\build\LunaTranslator\ /e /y /I
del ..\build\LunaTranslator\LunaTranslator\qt5qml.dll
del ..\build\LunaTranslator\LunaTranslator\qt5qmlmodels.dll
del ..\build\LunaTranslator\LunaTranslator\qt5quick.dll
del ..\build\LunaTranslator\LunaTranslator\qt5printsupport.dll
del ..\build\LunaTranslator\LunaTranslator\qt5websockets.dll
del ..\build\LunaTranslator\LunaTranslator\qt5dbus.dll
del ..\build\LunaTranslator\LunaTranslator\qt5multimedia.dll
del ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\platforms\qminimal.dll
del ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\platforms\qoffscreen.dll
del ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\platforms\qwebgl.dll
rmdir /S /Q ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\mediaservice
rmdir /S /Q ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\printsupport
rmdir /S /Q ..\build\LunaTranslator\LunaTranslator\PyQt5\qt-plugins\imageformats 
del ..\build\LunaTranslator\LunaTranslator\libssl-1_1-x64.dll
del ..\build\LunaTranslator\LunaTranslator\libcrypto-1_1-x64.dll
xcopy ..\build\LunaTranslator\ C:\dataH\LunaTranslator /e /y /I
pause