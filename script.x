#!/bin/bash

# Script para instalar as bibliotecas necessárias para o programa
# Execute com permissões de superusuário (sudo ./install_dependencies.sh)

# Atualiza o sistema e instala o gerenciador de pacotes pip
sudo apt update
sudo apt install -y python3-pip

# Instala as bibliotecas necessárias
pip install tkinter matplotlib numpy opencv-python-headless

echo "Instalação concluída."

