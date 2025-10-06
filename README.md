# Projeto Integrado com SQLite - Sistema de Eventos

Arquivos principais (mantidos e integrados com POO e SQLite):
- cadastro_eventos.py  -> Evento, Workshop, Palestra e SistemaEventos (SQLite)
- inscricoes_participantes.py -> Participante e InscricoesParticipantes (usa SistemaEventos)
- funcoes.py -> Funções auxiliares e relatórios que usam SistemaEventos
- main.py -> Menu principal (mantido com pequenas adaptações para integração)
- testes.py -> Testes unitários com 11 casos (unittest)

Como rodar:
```bash
python main.py
```
Rodar testes:
```bash
python -m unittest testes.py
```

Observações:
- O banco SQLite `eventos.db` é criado automaticamente na primeira execução.
- Mantive as mensagens do menu praticamente iguais ao original; alterei apenas o mínimo necessário e com comentários nas linhas novas.
