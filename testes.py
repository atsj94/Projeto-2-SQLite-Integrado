import os
import unittest
import sqlite3
from cadastro_eventos import SistemaEventos, Workshop, Palestra
from inscricoes_participantes import InscricoesParticipantes

TEST_DB = "test_eventos.db"

class TestSistemaEventosSQLite(unittest.TestCase):
    def setUp(self):
        # remove DB de teste se existir para garantir ambiente limpo
        try:
            os.remove(TEST_DB)
        except FileNotFoundError:
            pass
        self.sistema = SistemaEventos(TEST_DB)

    def tearDown(self):
        try:
            os.remove(TEST_DB)
        except FileNotFoundError:
            pass

    def test_criar_evento_workshop(self):
        w = Workshop("WS Teste", "31/12/2099", "LocalX", 2, 100, "Notebook")
        eid = self.sistema.cadastrar_evento(w)
        self.assertIsInstance(eid, int)

    def test_criar_evento_palestra(self):
        p = Palestra("Palestra Teste", "31/12/2099", "LocalY", 3, 50, "Dr. X")
        eid = self.sistema.cadastrar_evento(p)
        self.assertIsInstance(eid, int)

    def test_validacao_data_invalida(self):
        with self.assertRaises(ValueError):
            Workshop("WS", "31-12-2020", "L", 2, 50, "Mat")  # formato inválido

    def test_inscricao_sucesso(self):
        w = Workshop("WS Ins", "31/12/2099", "L", 2, 80, "Material")
        eid = self.sistema.cadastrar_evento(w)
        pid = self.sistema.inscrever_participante("Ana", "ana@x.com", eid)
        self.assertIsInstance(pid, int)

    def test_inscricao_duplicada(self):
        w = Workshop("WS Dup", "31/12/2099", "L", 2, 80, "Material")
        eid = self.sistema.cadastrar_evento(w)
        self.sistema.inscrever_participante("Ana", "ana@x.com", eid)
        with self.assertRaises(ValueError):
            self.sistema.inscrever_participante("Ana2", "ana@x.com", eid)  # mesmo email

    def test_evento_lotado(self):
        w = Workshop("WS Lot", "31/12/2099", "L", 1, 80, "Mat")
        eid = self.sistema.cadastrar_evento(w)
        self.sistema.inscrever_participante("P1", "p1@x.com", eid)
        with self.assertRaises(ValueError):
            self.sistema.inscrever_participante("P2", "p2@x.com", eid)  # já lotado

    def test_cancelar_inscricao(self):
        w = Workshop("WS Canc", "31/12/2099", "L", 2, 80, "Mat")
        eid = self.sistema.cadastrar_evento(w)
        pid = self.sistema.inscrever_participante("Carlos", "carlos@x.com", eid)
        ok = self.sistema.cancelar_inscricao("carlos@x.com")
        self.assertTrue(ok)

    def test_checkin(self):
        w = Workshop("WS Check", "31/12/2099", "L", 2, 80, "Mat")
        eid = self.sistema.cadastrar_evento(w)
        pid = self.sistema.inscrever_participante("Lia", "lia@x.com", eid)
        res = self.sistema.realizar_checkin("lia@x.com")
        self.assertTrue(res)

    def test_receita_total(self):
        w = Workshop("WS Rec", "31/12/2099", "L", 3, 40, "Mat")
        eid = self.sistema.cadastrar_evento(w)
        self.sistema.inscrever_participante("A", "a@x.com", eid)
        self.sistema.inscrever_participante("B", "b@x.com", eid)
        receita = self.sistema.receita_evento("WS Rec")
        self.assertEqual(receita, 2 * 40)

    def test_listar_eventos_buscar(self):
        p = Palestra("Buscar", "31/12/2099", "L", 3, 50, "X")
        self.sistema.cadastrar_evento(p)
        result = self.sistema.buscar_eventos_por_categoria("Palestra")
        self.assertTrue(len(result) >= 1)

if __name__ == "__main__":
    unittest.main()
