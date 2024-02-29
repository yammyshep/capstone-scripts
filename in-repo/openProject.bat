@echo off

SET UE_VERSION=5.2

pushd %~dp0
SET "REPO_ROOT=%CD%"
popd


REM Update the project using SVN
ECHO Running 'svn update %REPO_ROOT%'...
svn update "%REPO_ROOT%"


REM Fetch the root of the Unreal Engine installation directory from the registry
FOR /F "usebackq tokens=3*" %%A IN (`REG QUERY "HKEY_CURRENT_USER\SOFTWARE\Epic Games\Unreal Engine\Builds" /v %UE_VERSION%`) DO (
    SET UE_ROOT=%%A %%B
)

IF NOT DEFINED UE_ROOT (
    IF EXIST "C:\Program Files\Epic Games\UE_%UE_VERSION%\" (
        SET "UE_ROOT=C:\Program Files\Epic Games\UE_%UE_VERSION%\"
    )
)

IF DEFINED UE_ROOT (
    ECHO Autodetected Unreal Engine %UE_VERSION% install at %UE_ROOT%
) ELSE (
    ECHO Failed to autodetect Unreal Engine %UE_VERSION% installation!
    PAUSE
    EXIT 1
)


REM Fetch uproject file path
FOR %%f IN ("%REPO_ROOT%\*.uproject") DO (
    SET "UPROJECT=%%f"
    BREAK
)

IF DEFINED UPROJECT (
    ECHO Found uproject file at %UPROJECT%
) else (
    ECHO Failed to find uproject file in directory %REPO_ROOT%
    PAUSE
    EXIT 1
)


REM Build the project's editor binaries
CALL "%UE_ROOT%\Engine\Build\BatchFiles\RunUAT.bat" BuildEditor -project="%UPROJECT%" -notools


REM Launch the editor
start "%UE_ROOT%\Engine\Binaries\Win64\UnrealEditor" "%UPROJECT%"
