#!/usr/bin/python3
import argparse
import requests
from bs4 import BeautifulSoup
import re

################################################################################
# Title     : HTML Parse.                                                      #
# Version   : 1.0                                                              #
# Date      : 27/06/2024                                                       #
# Tested on : Linux/Windows10                                                  #
# created by: Charli Castelli.                                                 #
# -----------------------------------------------------------------------------#
# Description:                                                                 #
#   Essa ferramenta analisa codigo fonte de paginas HTML.                      #
#   Extrai informações de links href, src, .js, .php...                        #
# -----------------------------------------------------------------------------#
# Release Note:                                                                #
#                                                                              #
################################################################################

# Constantes cores
RED = "\033[1;31m"
RESET = "\033[0;0m"
BOLD = "\033[;1m"
GREEN = "\033[32m"


# Icones para mensagens
iconError = BOLD + RED + "[-]" + RESET
head = "-"*53 # Linha de separação para saídas.

banner = (GREEN + '''
╔═════════════════════════════════════════════════════╗
║ _   _ _____ __  __ _       ____                     ║
║| | | |_   _|  \/  | |     |  _ \ __ _ _ __ ___  ___ ║
║| |_| | | | | |\/| | |     | |_) / _` | '__/ __|/ _ \║
║|  _  | | | | |  | | |___  |  __/ (_| | |  \__ \  __/║
║|_| |_| |_| |_|  |_|_____| |_|   \__,_|_|  |___/\___|║
╚═════════════════════════════════════════════════════╝
''' + RESET)

print(banner)


# Função principal que extrai links de uma página HTML
def extract_links(url, file_types, include_href, include_all_files, include_src):
    try:
        # Faz a requisição HTTP para obter o conteúdo da página
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Listas para armazenar os links encontrados
        href_links = []
        file_links = []
        all_links = []
        src_links = []

        # Coleta todos os links de arquivos se a opção foi especificada
        if include_href or include_all_files:
            for link in soup.find_all('a', href=True):
                href = link['href']
                if not href.startswith('#'):  # Filtra âncoras internas
                    href_links.append(href)

        # Coleta todos os links de arquivos se a opção foi especificada
        if include_all_files:
            for tag in soup.find_all(['script', 'img', 'link', 'a']):
                if 'src' in tag.attrs:
                    all_links.append(tag['src'])
                if 'href' in tag.attrs:
                    href = tag['href']
                    if not href.startswith('#'):  # Filtra âncoras internas
                        all_links.append(href)

        # Coleta links de arquivos específicos com base nos tipos fornecidos
        if file_types:
            file_types_regex = '|'.join([re.escape(file_type) for file_type in file_types])
            for tag in soup.find_all(True):
                for attr in ['src', 'href']:
                    if attr in tag.attrs and re.search(rf'({file_types_regex})$', tag[attr]):
                        file_links.append(tag[attr])

        # Coleta links dos atributos 'src' se a opção foi especificada
        if include_src:
            for tag in soup.find_all(True):
                if 'src' in tag.attrs:
                    src_links.append(tag['src'])
        
        return href_links, file_links, all_links, src_links
        
    except requests.RequestException as e:
        print(f"Erro ao acessar a URL: {e}")
        return [], [], [], []
    
# Classe personalizada para exibir ajuda de forma customizada
class CustomHelpParser(argparse.ArgumentParser):
        def print_help(self):
            # Espaçamentos personalizados para formatação da mensagem de ajuda
            space1 = " "*7
            space2 = " "*5
            space3 = " "*8
            space4 = " "*1
            space5 = " "*10
            space6 = " "*11

            # Mensagens de ajuda formatadas
            text1 = f"-h,--help {space1} Help"
            text2 = f"-u,--url {space3} URL da pagina a ser analisada"
            text3 = f"-f,--file-types {space4} Tipos de arquivos a serem considerados (por exemplo: .js .php .html)"
            text4 = f"--href {space5} Incluir links do atributo 'href'"
            text5 = f"--all-files {space2} Incluir todos os arquivos"
            text6 = f"--src {space6} Incluir links do atributo 'src'"

            print("\nFerramenta extrai links de pagina HTML.\n")
            print(BOLD + f'{"Option":<17} {"Meaning":<10}' + RESET)
            custom_help_message = f"{text1}\n{text2}\n{text3}\n{text4}\n{text5}\n{text6}\n"
            print(custom_help_message)

        def error(self, message):
            msg1 = "python3 html_parser.py -u <http://url> --href -f .js"
            msg2 = "python3 html_parser.py"
            self.exit(2, f"\n{iconError} Exemplo de uso da ferramenta:\n{msg1}\n{msg2}\n\n{message}\n\n")



if __name__ == "__main__":
    # Criação do parser de argumentos
    parser = CustomHelpParser(description="Extrai links de uma página HTML")
    parser.add_argument("-u", "--url", required=True, help="URL da página a ser analisada")
    parser.add_argument("-f", "--file-types", nargs="*", help="Tipos de arquivos a serem considerados (por exemplo: .js .php .html)")
    parser.add_argument("--href", action="store_true", help="Incluir links do atributo 'href'")
    parser.add_argument("--all-files", action="store_true", help="Incluir todos os arquivos")
    parser.add_argument("--src", action="store_true", help="Incluir links do atributo 'src'")

    # Análise dos argumentos fornecidos pelo usuário
    args = parser.parse_args()

    if not args.file_types and not args.href and not args.all_files and not args.src:
        print(f"\n{iconError} Pelo menos um dos argumentos de varredura (-f, --href, --all-files, --src) deve ser fornecido.\n")
    else:
        url = args.url
        file_types = args.file_types
        include_href = args.href
        include_all_files = args.all_files
        include_src = args.src

        # Chamada da função principal para extrair links
        href_links, file_links, all_links, src_links = extract_links(url, file_types, include_href, include_all_files, include_src)

        # Exibição dos links encontrados, organizados por categoria
        if include_href:
            print(head)
            print(BOLD + f"Links encontrados no atributo <href>:" + RESET)
            print(head)
            if href_links:
                for link in href_links:
                    print(link)
                print()
            else:
                print("Nenhum link encontrado no atributo <href>.\n")

        if file_types:
            print(head)
            print(BOLD + f"Links de arquivos especificados: {file_types}" + RESET)
            print(head)
            if file_links:
                for link in file_links:
                    print(link)
                print()
            else:
                print("Nenhum arquivo especificado foi encontrado.\n")

        if include_all_files:
            print(head)
            print(BOLD + f"Todos os links de arquivos encontrados:" + RESET)
            print(head)
            if all_links:
                for link in all_links:
                    print(link)
                print()
            else:
                print("Nenhum link de arquivo foi encontrado.\n")

        if include_src:
            print(head)
            print(BOLD + f"Links encontrados no atributo <src>:" + RESET)
            print(head)
            if src_links:
                for link in src_links:
                    print(link)
                print()
            else:
                print("Nenhum link encontrado no atributo <src>.\n")
