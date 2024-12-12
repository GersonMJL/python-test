#!/bin/bash

# Verifica se todos os argumentos foram fornecidos
if [ $# -ne 3 ]; then
    echo "Uso: $0 <arquivo_entrada> <min_msgs> <max_msgs>"
    exit 1
fi

# Verifica se o arquivo de entrada existe
if [ ! -f "$1" ]; then
    echo "Arquivo de entrada não encontrado!"
    exit 1
fi

# Filtra usuários com mensagens entre o intervalo especificado
awk -v min="$2" -v max="$3" '
$3 >= min && $3 <= max {print $0}
' "$1"
