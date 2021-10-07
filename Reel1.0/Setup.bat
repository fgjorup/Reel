@ECHO off
ECHO @ECHO off > Run_Reel.bat
ECHO TITLE Reel >> Run_Reel.bat
ECHO CD %~dp0 >> Run_Reel.bat
ECHO ECHO Opening Reel 1.0... >> Run_Reel.bat
FOR %%i IN (python.exe) DO (
    IF EXIST "%%~$PATH:i" (
       ECHO "%%~$PATH:i" Refinement_evaluator_ver1.0.py >> Run_Reel.bat
    ) ELSE (
        ECHO python.exe Refinement_evaluator_ver1.0.py >> Run_Reel.bat
        ECHO ATTENTION!
        ECHO "python.exe" path not found! Please manually correct it in "Run_Reel.bat" LINE 5
        PAUSE
    )
)
ECHO PAUSE >> Run_Reel.bat
ECHO EXIT >> Run_Reel.bat
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%~dp0\Reel1.0.lnk');$s.TargetPath='%~dp0\Run_Reel.bat';$s.IconLocation='%~dp0\_lib\icons\Main.ico';$s.Save()"
