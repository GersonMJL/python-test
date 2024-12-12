#!/bin/bash

# Verifica se o arquivo de entrada foi fornecido
if [ $# -eq 0 ]; then
    echo "Uso: $0 <arquivo_entrada> [-min]"
    exit 1
fi

# Verifica se o arquivo de entrada existe
if [ ! -f "$1" ]; then
    echo "Arquivo de entrada não encontrado!"
    exit 1
fi

# Determina se deve encontrar o tamanho máximo ou mínimo
if [ "$2" == "-min" ]; then
    # Encontra o usuário com o menor tamanho
    awk 'BEGIN {menor_tamanho = "999999999"; usuario_menor = ""}
    {
        if ($5 < menor_tamanho || menor_tamanho == "999999999") {
            menor_tamanho = $5
            usuario_menor = $0
        }
    }
    END {print usuario_menor}' "$1"
else
    # Encontra o usuário com o maior tamanho
    awk 'BEGIN {maior_tamanho = 0; usuario_maior = ""}
    {
        if ($5 > maior_tamanho) {
            maior_tamanho = $5
            usuario_maior = $0
        }
    }
    END {print usuario_maior}' "$1"
fi
