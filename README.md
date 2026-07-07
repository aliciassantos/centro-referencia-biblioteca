# Centro de Referência UESPI

## Estrutura do projeto
```
centro-referencia-biblioteca/
├── .venv/                      # Ambiente virtual do Python (dependências)
├── alembic/                    # Configurações de migração do banco de dados
│   ├── versions/               # Histórico de scripts de migração (.py)
│   ├── env.py                  # Script de execução do Alembic
│   ├── README                  # Documentação padrão do Alembic
│   └── script.py.mako          # Template para novas migrações
├── app/                        # Código-fonte principal da aplicação
│   ├── __init__.py             # Inicializador do pacote Python
│   ├── crud.py                 # Funções utilitárias de banco (opcional/auxiliar)
│   ├── database.py             # Configuração da engine e SessionLocal do SQLAlchemy
│   ├── main.py                 # Rotas do FastAPI (GET, POST, PUT, DELETE) e lógica do app
│   ├── models.py               # Modelos das tabelas do banco (Instrucao, Usuario, etc.)
│   ├── schemas.py              # Schemas de validação de dados do Pydantic (InstrucaoCreate, etc.)
│   └── security.py             # Funções de hashing de senhas e geração/validação de tokens JWT
├── .env                        # Variáveis de ambiente protegidas (senhas, chaves secretas)
├── .gitignore                  # Arquivos que o Git deve ignorar (ex: .venv, .env)
├── alembic.ini                 # Arquivo de configuração global do Alembic
├── ESCOPO.md                   # Documentação das fases e regras de negócio do projeto
├── LICENSE                     # Licença de uso do software
├── README.md                   # Instruções de instalação e execução do projeto
├── requirements.txt            # Lista de dependências instaladas (FastAPI, SQLAlchemy, etc.)
├── seed.py                     # Script para popular o banco de dados inicialmente
└── test_queries.py             # Scripts rápidos de teste para consultas de dados
```
