"""
funcoes.py
Funções auxiliares (validadores, limpar tela, pausar e relatórios).
As alterações foram feitas para chamar o SistemaEventos para relatórios (SQLite).
"""

import os
from datetime import datetime
from cadastro_eventos import SistemaEventos

def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")

def pausar(msg="\nPressione ENTER para voltar..."):
    input(msg)
    limpar_tela()

def validar_texto(campo):
    while True:
        valor = input(f"{campo}: ").strip()
        if valor:
            return valor
        else:
            input(f"ERRO! : O campo '{campo}' não pode ficar em branco. Pressione ENTER para tentar novamente.")

def validar_inteiro(campo):
    while True:
        valor = input(f"{campo}: ").strip()
        if valor.isdigit() and int(valor) > 0:
            return int(valor)
        else:
            input(f"ERRO! : O campo '{campo}' deve ser um número inteiro positivo. Pressione ENTER para tentar novamente.")

def validar_float(campo):
    while True:
        valor = input(f"{campo}: ").strip()
        try:
            numero = float(valor)
            if numero >= 0:
                return numero
            else:
                input(f"ERRO! : O campo '{campo}' deve ser um número maior ou igual a zero. Pressione ENTER para tentar novamente.")
        except ValueError:
            input(f"ERRO! : O campo '{campo}' deve ser numérico. Pressione ENTER para tentar novamente.")

def validar_data(campo):
    while True:
        valor = input(f"{campo} (DD/MM/AAAA): ").strip()
        try:
            data = datetime.strptime(valor, "%d/%m/%Y")
            if data.date() < datetime.today().date():
                input(f"ERRO! : A data não pode ser anterior à data atual. Pressione ENTER para tentar novamente.")
            else:
                return data.strftime("%d/%m/%Y")
        except ValueError:
            input(f"ERRO! : O campo '{campo}' deve estar no formato DD/MM/AAAA. Pressione ENTER para tentar novamente.")

def relatorios(sistema: SistemaEventos):
    # recebe o gerenciador SistemaEventos para ler diretamente do DB (nova integração)
    while True:
        print("##### RELATÓRIOS #####")
        print("1 - Número total de inscritos por evento")
        print("2 - Lista de eventos com vagas disponíveis")
        print("3 - Receita total por evento")
        print("0 - Voltar ao menu principal")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            print("\n#### INSCRITOS POR EVENTO ####")
            linha = sistema.total_inscritos_por_evento()
            if not linha:
                print("Nenhum evento cadastrado.")
            else:
                for nome, total in linha:
                    print(f"{nome}: {total} inscritos")
            pausar()

        elif opcao == "2":
            print("\n#### EVENTOS COM VAGAS DISPONÍVEIS ####")
            rows = sistema.eventos_com_vagas()
            if not rows:
                print("Nenhum evento com vagas.")
            else:
                for eid, nome, vagas in rows:
                    print(f"{nome} -> {vagas} vagas restantes")
            pausar()

        elif opcao == "3":
            print("\n##### RECEITA TOTAL POR EVENTO #####")
            termos = sistema.total_inscritos_por_evento()
            if not termos:
                print("Nenhum evento cadastrado.")
            else:
                for nome, _ in termos:
                    receita = sistema.receita_evento(nome)
                    print(f"{nome}: R${receita:.2f}")
            pausar()

        elif opcao == "0":
            limpar_tela()
            break
        else:
            input("Opção INVÁLIDA, pressione ENTER para tentar novamente.")
            limpar_tela()
