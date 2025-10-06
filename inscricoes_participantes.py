"""
inscricoes_participantes.py
Define a classe Participante leve e a classe InscricoesParticipantes que utiliza o SistemaEventos
para persistência (SQLite). Alterações comentadas nas linhas novas.
"""

from cadastro_eventos import SistemaEventos

class Participante:
    def __init__(self, nome: str, email: str, checkin: bool = False, participante_id: int = None, evento_id: int = None):
        # atributos privados (encapsulamento)
        self.__id = participante_id
        self.__nome = nome
        self.__email = email
        self.__checkin = bool(checkin)
        self.__evento_id = evento_id

    def get_nome(self): return self.__nome
    def get_email(self): return self.__email
    def get_checkin(self): return self.__checkin
    def get_evento_id(self): return self.__evento_id

    def set_nome(self, nome): self.__nome = nome
    def set_email(self, email): self.__email = email
    def set_checkin(self, valor: bool): self.__checkin = bool(valor)

class InscricoesParticipantes:
    def __init__(self, nome: str, email: str, evento_id: int, db_path: str = "eventos.db"):
        # utiliza o gerenciador SistemaEventos para realizar a inscrição no banco (nova abordagem)
        sistema = SistemaEventos(db_path)  # novo: cria/usa o gerenciador que cuida do DB
        # tenta inscrever, pode lançar ValueError em caso de duplicidade ou lotação
        participante_id = sistema.inscrever_participante(nome, email, evento_id)
        # armazena info local (não estritamente necessária, mas útil para compatibilidade)
        self.nome = nome
        self.email = email
        self.id = participante_id
        self.evento_id = evento_id

    def cancelar_inscricao(self):
        sistema = SistemaEventos()  # usa o gerenciador para cancelar no DB
        sucesso = sistema.cancelar_inscricao(self.email)
        return sucesso

    def realizar_checkin(self):
        sistema = SistemaEventos()
        res = sistema.realizar_checkin(self.email)
        return res

    def __str__(self):
        return f"Participante: {self.nome} | Email: {self.email} | Evento ID: {self.evento_id}"
