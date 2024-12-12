#!/bin/bash

# Verifica se o arquivo de entrada foi fornecido
if [ $# -eq 0 ]; then
    echo "Uso: $0 <arquivo_entrada> [-desc]"
    exit 1
fi

# Verifica se o arquivo de entrada existe
if [ ! -f "$1" ]; then
    echo "Arquivo de entrada não encontrado!"
    exit 1
fi

# Verifica o parâmetro de ordem decrescente
if [ "$2" == "-desc" ]; then
    # Ordena por nome de usuário em ordem decrescente
    sort -r -k1 "$1"
else
    # Ordena por nome de usuário em ordem crescente
    sort -k1 "$1"
fi
