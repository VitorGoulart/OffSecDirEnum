# Função:

Script de automação criada em python para enumeração de diretórios e arquivos em servidores web.

## Requisitos:

* httpx

## Como utilizar:

Linux:
`python3 prog.py <URL-alvo> -w <path-para-wordlist> [-x extensões-de-arquivos]`

Windows:
`python prog.py <URL-alvo> -w <path-para-wordlist> [-x extensões-de-arquivos]`

Com alvo de testes, foi utilizando um servidor http python na pasta test-site/ com o comando:
`python -m http.server 8000 --bind 127.0.0.1`

Em seguida, foi executado o script com:
`python prog.py http://127.0.0.1:8000 -w wordlist.txt -x html`

