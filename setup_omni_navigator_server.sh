#!/bin/bash

echo "Iniciando la configuración del servidor Omni-Navigator..."

# Asegurarse de que Python y pip estén instalados
if ! command -v python3 &> /dev/null
then
    echo "Python3 no encontrado. Por favor, instálelo."
    exit 1
fi

if ! command -v pip3 &> /dev/null
then
    echo "pip3 no encontrado. Por favor, instálelo."
    exit 1
fi

# Instalar dependencias de Python
echo "Instalando dependencias de Python..."
pip3 install -r requirements.txt

# Instalar navegadores de Playwright
echo "Instalando navegadores de Playwright..."
playwright install

# Iniciar el servidor Flask en segundo plano usando nohup
echo "Iniciando el servidor Omni-Navigator en segundo plano..."
nohup python3 app.py > omni_navigator_server.log 2>&1 &
echo $! > omni_navigator_server.pid
echo "Servidor Omni-Navigator iniciado. PID guardado en omni_navigator_server.pid"
echo "Los logs se encuentran en omni_navigator_server.log"

echo "Configuración del servidor Omni-Navigator completada."
echo "Asegúrese de que el puerto 5000 esté abierto en su firewall si es necesario."
