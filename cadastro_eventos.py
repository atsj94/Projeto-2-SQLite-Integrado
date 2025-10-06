"""
cadastro_eventos.py
Versão integrada (POO + SQLite) mantendo a lógica original. 
Foram adicionadas as classes Evento, Workshop, Palestra e SistemaEventos.
Novas linhas e alterações possuem comentários explicativos.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

DB_PATH = "eventos.db"  # arquivo SQLite (criado automaticamente)

# ----------------------- Classe Evento (superclasse) -----------------------
class Evento:
    def __init__(self, nome: str, data: str, local: str, capacidade_maxima: int, categoria: str, preco_ingresso: float, extra: Optional[str] = None, evento_id: Optional[int] = None):
        # atributos privados (encapsulamento) - novos
        self.__id = evento_id  # id no banco (pode ser None antes de salvar)
        self.__nome = nome
        # valida e converte data
        try:
            data_obj = datetime.strptime(data, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Data INVÁLIDA! Use o formato DD/MM/AAAA.")
        if data_obj.date() < datetime.today().date():
            raise ValueError("A data do evento não pode ser anterior à data atual.")
        self.__data = data_obj
        # valida capacidade e preço
        if not isinstance(capacidade_maxima, int) or capacidade_maxima <= 0:
            raise ValueError("A capacidade máxima deve ser um número inteiro positivo.")
        self.__capacidade_maxima = capacidade_maxima
        if not isinstance(preco_ingresso, (int, float)) or preco_ingresso < 0:
            raise ValueError("O preço do ingresso deve ser numérico e >= 0.")
        self.__preco_ingresso = float(preco_ingresso)

        self.__local = local
        self.__categoria = categoria
        self.__extra = extra  # campo extra para subclasse (material/palestrante)

    # ------------------ Getters e Setters (encapsulamento) ------------------
    def get_id(self): return self.__id
    def get_nome(self): return self.__nome
    def get_data(self): return self.__data
    def get_local(self): return self.__local
    def get_capacidade(self): return self.__capacidade_maxima
    def get_categoria(self): return self.__categoria
    def get_preco(self): return self.__preco_ingresso
    def get_extra(self): return self.__extra

    def set_nome(self, nome): self.__nome = nome
    def set_local(self, local): self.__local = local
    def set_capacidade(self, capacidade):
        if isinstance(capacidade, int) and capacidade >= 0:
            self.__capacidade_maxima = capacidade
        else:
            raise ValueError("Capacidade inválida.")
    def set_preco(self, preco):
        if isinstance(preco, (int, float)) and preco >= 0:
            self.__preco_ingresso = float(preco)
        else:
            raise ValueError("Preço inválido.")

    # método polimórfico (sobrescrito nas subclasses)
    def detalhes(self):
        return (f"Evento: {self.__nome}\n"
                f"Data: {self.__data.strftime('%d/%m/%Y')}\n"
                f"Local: {self.__local}\n"
                f"Capacidade Máxima: {self.__capacidade_maxima}\n"
                f"Categoria: {self.__categoria}\n"
                f"Preço do Ingresso: R${self.__preco_ingresso:.2f}")

# ----------------------- Subclasses -----------------------
class Workshop(Evento):
    def __init__(self, nome, data, local, capacidade_maxima, preco_ingresso, material_necessario, evento_id: Optional[int] = None):
        # repassa categoria "Workshop" para a superclasse
        super().__init__(nome, data, local, capacidade_maxima, "Workshop", preco_ingresso, extra=material_necessario, evento_id=evento_id)

    # sobrescrita do método detalhes (polimorfismo)
    def detalhes(self):
        base = super().detalhes()
        return base + f"\nMaterial: {self.get_extra()}"

class Palestra(Evento):
    def __init__(self, nome, data, local, capacidade_maxima, preco_ingresso, palestrante, evento_id: Optional[int] = None):
        super().__init__(nome, data, local, capacidade_maxima, "Palestra", preco_ingresso, extra=palestrante, evento_id=evento_id)

    def detalhes(self):
        base = super().detalhes()
        return base + f"\nPalestrante: {self.get_extra()}"

# ----------------------- SistemaEventos (gerenciador + persistência) -----------------------
class SistemaEventos:
    def __init__(self, db_path: str = DB_PATH):
        self.__db_path = db_path
        # cria as tabelas caso não existam (criação automática) - nova funcionalidade
        self.__criar_tabelas()

    def __conexao(self):
        # cria conexão com SQLite (método privado)
        return sqlite3.connect(self.__db_path)

    def __criar_tabelas(self):
        # cria as tabelas eventos e participantes, se não existirem
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS eventos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    data TEXT NOT NULL,
                    local TEXT NOT NULL,
                    capacidade INTEGER NOT NULL,
                    categoria TEXT NOT NULL,
                    preco REAL NOT NULL,
                    extra TEXT,
                    tipo TEXT NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS participantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    checkin INTEGER DEFAULT 0,
                    evento_id INTEGER,
                    FOREIGN KEY(evento_id) REFERENCES eventos(id)
                )
            """)
            conn.commit()

    # ----------------------- CRUD de Eventos -----------------------
    def cadastrar_evento(self, evento: Evento):
        # insere evento no banco (mantendo compatibilidade com a API anterior)
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO eventos (nome, data, local, capacidade, categoria, preco, extra, tipo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (evento.get_nome(), evento.get_data().strftime("%d/%m/%Y"), evento.get_local(),
                  evento.get_capacidade(), evento.get_categoria(), evento.get_preco(), evento.get_extra(), evento.__class__.__name__))
            conn.commit()
            evento_id = cur.lastrowid
            return evento_id  # id do registro criado

    def listar_eventos(self) -> List[Evento]:
        # retorna a lista de objetos Evento/Workshop/Palestra representando os registros do DB
        eventos = []
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nome, data, local, capacidade, categoria, preco, extra, tipo FROM eventos")
            rows = cur.fetchall()
            for row in rows:
                eid, nome, data, local, capacidade, categoria, preco, extra, tipo = row
                if tipo == "Workshop":
                    eventos.append(Workshop(nome, data, local, capacidade, preco, extra, evento_id=eid))
                else:
                    eventos.append(Palestra(nome, data, local, capacidade, preco, extra, evento_id=eid))
        return eventos

    def buscar_eventos_por_categoria(self, categoria: str) -> List[Evento]:
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nome, data, local, capacidade, categoria, preco, extra, tipo FROM eventos WHERE LOWER(categoria)=?", (categoria.lower(),))
            rows = cur.fetchall()
            resultados = []
            for row in rows:
                eid, nome, data, local, capacidade, categoria, preco, extra, tipo = row
                if tipo == "Workshop":
                    resultados.append(Workshop(nome, data, local, capacidade, preco, extra, evento_id=eid))
                else:
                    resultados.append(Palestra(nome, data, local, capacidade, preco, extra, evento_id=eid))
            return resultados

    def buscar_eventos_por_data(self, data_str: str) -> List[Evento]:
        # aceita data no formato DD/MM/AAAA
        try:
            datetime.strptime(data_str, "%d/%m/%Y")
        except ValueError:
            return []
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nome, data, local, capacidade, categoria, preco, extra, tipo FROM eventos WHERE data=?", (data_str,))
            rows = cur.fetchall()
            resultados = []
            for row in rows:
                eid, nome, data, local, capacidade, categoria, preco, extra, tipo = row
                if tipo == "Workshop":
                    resultados.append(Workshop(nome, data, local, capacidade, preco, extra, evento_id=eid))
                else:
                    resultados.append(Palestra(nome, data, local, capacidade, preco, extra, evento_id=eid))
            return resultados

    # ----------------------- Participantes -----------------------
    def inscrever_participante(self, nome: str, email: str, evento_id: int):
        # verifica vagas, duplicidade e insere participante no DB
        with self.__conexao() as conn:
            cur = conn.cursor()
            # busca capacidade e número de inscritos
            cur.execute("SELECT capacidade FROM eventos WHERE id=?", (evento_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError("Evento não encontrado.")
            capacidade = row[0]
            cur.execute("SELECT COUNT(*) FROM participantes WHERE evento_id=?", (evento_id,))
            inscritos = cur.fetchone()[0]
            if inscritos >= capacidade:
                raise ValueError("O evento já está lotado.")

            # verifica duplicidade de email para o mesmo evento
            cur.execute("SELECT id FROM participantes WHERE evento_id=? AND LOWER(email)=?", (evento_id, email.lower()))
            if cur.fetchone():
                raise ValueError("Esse e-mail já está inscrito neste evento.")

            cur.execute("INSERT INTO participantes (nome, email, checkin, evento_id) VALUES (?, ?, 0, ?)", (nome, email, evento_id))
            conn.commit()
            return cur.lastrowid

    def cancelar_inscricao(self, email: str):
        # remove participante por email (em qualquer evento)
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM participantes WHERE LOWER(email)=?", (email.lower(),))
            row = cur.fetchone()
            if not row:
                return False
            cur.execute("DELETE FROM participantes WHERE id=?", (row[0],))
            conn.commit()
            return True

    def realizar_checkin(self, email: str):
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, checkin FROM participantes WHERE LOWER(email)=?", (email.lower(),))
            row = cur.fetchone()
            if not row:
                return False
            if row[1] == 1:
                return "Já fez check-in"
            cur.execute("UPDATE participantes SET checkin=1 WHERE id=?", (row[0],))
            conn.commit()
            return True

    # ----------------------- Relatórios / consultas -----------------------
    def total_inscritos_por_evento(self):
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT e.nome, COUNT(p.id) as total
                FROM eventos e LEFT JOIN participantes p ON e.id = p.evento_id
                GROUP BY e.id
            """)
            return cur.fetchall()

    def eventos_com_vagas(self):
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT e.id, e.nome, e.capacidade - COUNT(p.id) as vagas_restantes
                FROM eventos e LEFT JOIN participantes p ON e.id = p.evento_id
                GROUP BY e.id HAVING vagas_restantes > 0
            """)
            return cur.fetchall()

    def receita_evento(self, nome_evento: str):
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT e.preco, COUNT(p.id) FROM eventos e LEFT JOIN participantes p ON e.id = p.evento_id WHERE LOWER(e.nome)=?
                GROUP BY e.id
            """, (nome_evento.lower(),))
            row = cur.fetchone()
            if not row:
                return 0.0
            preco, qtd = row
            return preco * qtd

    def get_evento_por_id(self, evento_id: int) -> Optional[Evento]:
        with self.__conexao() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, nome, data, local, capacidade, categoria, preco, extra, tipo FROM eventos WHERE id=?", (evento_id,))
            row = cur.fetchone()
            if not row:
                return None
            eid, nome, data, local, capacidade, categoria, preco, extra, tipo = row
            if tipo == "Workshop":
                return Workshop(nome, data, local, capacidade, preco, extra, evento_id=eid)
            return Palestra(nome, data, local, capacidade, preco, extra, evento_id=eid)
