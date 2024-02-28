@echo off

SET UE_VERSION=5.2

REM Update the project using SVN
ECHO Running 'svn update %~dp0'...
svn update %~dp0


REM Fetch the root of the Unreal Engine installation directory from the registry
FOR /F "usebackq tokens=3*" %%A IN (`REG QUERY "HKEY_CURRENT_USER\SOFTWARE\Epic Games\Unreal Engine\Builds" /v %UE_VERSION%`) DO (
    SET UE_ROOT=%%A %%B
)

IF DEFINED UE_ROOT (
    ECHO Autodetected Unreal Engine %UE_VERSION% install at %UE_ROOT%
) ELSE (
    ECHO Failed to autodetect Unreal Engine %UE_VERSION% installation!
    PAUSE
    EXIT 1
)


REM Fetch uproject file path
FOR %%f IN (%~dp0/*.uproject) DO (
    SET "UPROJECT=%%f"
    BREAK
)

IF DEFINED UPROJECT (
    ECHO Found uproject file at %UPROJECT%
) else (
    ECHO Failed to find uproject file in directory %~dp0
    PAUSE
    EXIT 1
)


REM Build the project's editor binaries
CALL "%UE_ROOT%\Engine\Build\BatchFiles\RunUAT.bat" BuildEditor -project="%UPROJECT%" -notools


REM Launch the editor
start "%UE_ROOT%\Engine\Binaries\Win64\UnrealEditor" "%UPROJECT%"
