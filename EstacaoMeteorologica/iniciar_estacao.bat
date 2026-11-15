@echo off
setlocal
title Inicializador - Estacao Meteorologica

REM Usa a pasta backend ao lado deste .bat, em qualquer computador.
REM Se mudar a estrutura de pastas, ajuste este caminho.
set "BACKEND=%~dp0backend"

REM Confere se os arquivos existem antes de iniciar.
if not exist "%BACKEND%\receptor_mqtt.py" (
    echo ERRO: receptor_mqtt.py nao encontrado em "%BACKEND%".
    pause
    exit /b 1
)
if not exist "%BACKEND%\api.py" (
    echo ERRO: api.py nao encontrado em "%BACKEND%".
    pause
    exit /b 1
)

REM Confere se o Python esta disponivel.
where python >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH.
    pause
    exit /b 1
)

REM Verifica se a porta MQTT local esta acessivel.
powershell -NoProfile -Command "if (-not (Test-NetConnection -ComputerName 127.0.0.1 -Port 1883 -InformationLevel Quiet -WarningAction SilentlyContinue)) { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo AVISO: Mosquitto nao respondeu na porta 1883.
    echo Confira o servico Mosquitto em services.msc.
    pause
    exit /b 1
)

REM Inicia o receptor e a API em janelas separadas.
REM Feche instancias anteriores antes de usar este inicializador.
start "Receptor MQTT - Estacao" /D "%BACKEND%" cmd /k "python receptor_mqtt.py"
start "API Flask - Estacao" /D "%BACKEND%" cmd /k "python api.py"

REM Aguarda alguns segundos para a API iniciar.
timeout /t 4 /nobreak >nul

REM Abre o painel no navegador padrao.
start "" "http://127.0.0.1:5000"

echo Dashboard aberto. Mantenha as duas janelas de servico abertas.
echo Para encerrar, use Ctrl+C em cada janela.
pause
endlocal
