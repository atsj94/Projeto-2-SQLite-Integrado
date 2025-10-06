"""
main.py
Menu principal adaptado para usar SistemaEventos (SQLite) mantendo as mensagens originais.
Novas linhas comentadas para indicar integração com POO e DB.
"""

from cadastro_eventos import SistemaEventos, Workshop, Palestra  # agora importamos as classes POO
from inscricoes_participantes import InscricoesParticipantes  # usa o novo fluxo que grava no DB
from funcoes import *

def menu():
    sistema = SistemaEventos()  # novo: gerenciador que cria/abre o DB automaticamente

    while True:
        print("####### MENU PRINCIPAL #######")
        print("| 1 - Cadastrar evento       |")
        print("| 2 - Listar eventos         |")
        print("| 3 - Inscrever participante |")
        print("| 4 - Realizar check-in      |")
        print("| 5 - Cancelar inscrição     |")
        print("| 6 - Relatórios             |")
        print("| 0 - Sair                   |")

        opcao = input("\nEscolha uma opção: ")

        if opcao == "1":  # CADASTRAR EVENTO 
            while True:
                try:
                    tipo = validar_texto("Tipo (workshop/palestra)").strip().lower()
                    nome = validar_texto("\nNome do evento")
                    data = validar_data("Data do evento")
                    local = validar_texto("Local do evento")
                    capacidade = validar_inteiro("Capacidade máxima")
                    categoria = validar_texto("Categoria")
                    preco = validar_float("Preço do ingresso")

                    # Mantivemos fluxo semelhante: criei o objeto correto (Workshop ou Palestra)
                    if tipo.startswith("w"):
                        material = validar_texto("Material necessário")
                        evento = Workshop(nome, data, local, capacidade, preco, material)  # novo objeto Workshop
                    else:
                        palestrante = validar_texto("Palestrante")
                        evento = Palestra(nome, data, local, capacidade, preco, palestrante)  # novo objeto Palestra

                    # usei o gerenciador SistemaEventos para salvar no DB (nova linha)
                    evento_id = sistema.cadastrar_evento(evento)  # retorna id do evento criado
                    print(f"\nEvento '{evento.get_nome()}' cadastrado com SUCESSO! (ID: {evento_id})")
                except Exception as e:
                    input(f"Erro: {e}. Pressione ENTER para tentar novamente.")

                escolha = input("\nDeseja cadastrar outro evento? (s/n): ").strip().lower()
                if escolha != "s":
                    limpar_tela()
                    break

        elif opcao == "2":  # LISTAR EVENTOS
            print("\n#### LISTA DE EVENTOS ####")
            eventos = sistema.listar_eventos()  # agora vinda do DB
            if not eventos:
                print("Nenhum evento cadastrado.")
            else:
                for evento in eventos:
                    print(evento.detalhes())  # método polimórfico

            escolha = input("\nVocê deseja fazer uma busca de evento por categoria ou data? (s/n): ").strip().lower()
            if escolha == "s":
                termo = input("Digite a categoria ou a data (DD/MM/AAAA): ").strip()
                resultados = []
                # busca por categoria
                resultados += sistema.buscar_eventos_por_categoria(termo)  # nova chamada
                # busca por data (string)
                resultados += sistema.buscar_eventos_por_data(termo)
                if resultados:
                    print("\n#### RESULTADOS DA BUSCA ####")
                    for evento in resultados:
                        print(evento.detalhes())
                else:
                    print("\nNenhum evento encontrado.")
                pausar()
            else:
                limpar_tela()

        elif opcao == "3":  # INSCREVER PARTICIPANTE
            while True:
                try:
                    eventos = sistema.listar_eventos()
                    if not eventos:
                        print("Nenhum evento cadastrado.")
                        pausar()
                        break

                    print("\n#### EVENTOS DISPONÍVEIS ####")
                    for i, evento in enumerate(eventos, start=1):
                        # busca quantidade de inscritos diretamente do DB para mostrar compatibilidade com o menu
                        from cadastro_eventos import SistemaEventos as _SE
                        se = _SE()
                        # calcula inscritos no evento
                        with se._SistemaEventos__conexao() as conn:  # NOTE: uso de método privado para compatibilidade (comentado)
                            cur = conn.cursor()
                            cur.execute("SELECT COUNT(*) FROM participantes WHERE evento_id=?", (evento.get_id(),))
                            inscritos = cur.fetchone()[0]
                        print(f"{i} - {evento.get_nome()} ({inscritos}/{evento.get_capacidade()})")

                    escolha = validar_inteiro("Escolha o número do evento") - 1
                    if escolha < 0 or escolha >= len(eventos):
                        input("Evento INVÁLIDO. Pressione ENTER para tentar novamente.")
                        continue

                    evento = eventos[escolha]
                    nome = validar_texto("Nome do participante")
                    email = validar_texto("E-mail do participante")

                    # Utiliza a classe InscricoesParticipantes que persiste no DB via SistemaEventos
                    inscrito = InscricoesParticipantes(nome, email, evento.get_id())
                    print(f"\nInscrição de {inscrito.nome} realizada com SUCESSO! (ID: {inscrito.id})")
                except Exception as e:
                    input(f"Erro: {e}. Pressione ENTER para tentar novamente.")

                nova_inscricao = input("\nVocê deseja inscrever mais um participante? (s/n): ").strip().lower()
                if nova_inscricao != "s":
                    limpar_tela()
                    break

        elif opcao == "4":  # REALIZAR CHECK-IN
            while True:
                try:
                    email = validar_texto("Digite o e-mail do participante")
                    res = sistema.realizar_checkin(email)  # usa SistemaEventos
                    if res is True:
                        print("Check-in realizado!")
                    elif res == "Já fez check-in":
                        print("Participante já fez check-in anteriormente.")
                    else:
                        print("Participante NÃO encontrado.")
                except Exception as e:
                    input(f"Erro: {e}. Pressione ENTER para tentar novamente.")

                mais_checkin = input("\nVocê deseja fazer mais algum Check-in? (s/n): ").strip().lower()
                if mais_checkin != "s":
                    limpar_tela()
                    break

        elif opcao == "5":  # CANCELAR INSCRIÇÃO
            while True:
                try:
                    email = validar_texto("Digite o e-mail do participante")
                    sucesso = sistema.cancelar_inscricao(email)  # usa SistemaEventos
                    if sucesso:
                        print("Inscrição cancelada.")
                    else:
                        print("Participante NÃO encontrado.")
                except Exception as e:
                    input(f"Erro: {e}. Pressione ENTER para tentar novamente.")

                mais_cancelar = input("\nVocê deseja cancelar mais uma inscrição? (s/n): ").strip().lower()
                if mais_cancelar != "s":
                    limpar_tela()
                    break

        elif opcao == "6":  # RELATÓRIOS
            limpar_tela()
            relatorios(sistema)  # passa o gerenciador para a função de relatórios

        elif opcao == "0":
            print("Obrigado por ter utilizado nosso sistema. Até a próxima.")
            break

        else:
            input("Opção INVÁLIDA, pressione ENTER para tentar novamente.")
            limpar_tela()

if __name__ == "__main__":
    limpar_tela()
    menu()
