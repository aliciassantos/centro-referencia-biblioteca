# Centro de Referência UESPI

## Estrutura do projeto
```
├── .venv/                  # Ambiente virtual do Python
├── app/                    # Pasta principal da aplicação
│   ├── __init__.py         # Inicializador do módulo Python
│   ├── crud.py             # Operações de banco de dados (Create, Read, Update, Delete)
│   ├── database.py         # Configuração da conexão com o MySQL e SessionLocal
│   ├── main.py             # Arquivo principal com as rotas do FastAPI
│   ├── models.py           # Modelos de tabelas do SQLAlchemy (DDL revisado)
│   └── schemas.py          # Schemas de validação de dados do Pydantic
├── .env                    # Variáveis de ambiente (credenciais do banco)
├── .gitignore              # Arquivos ignorados pelo Git (como .venv e .env)
├── ESCOPO.md               # Documentação do escopo do projeto
├── LICENSE                 # Licença do projeto (MIT)
├── README.md               # Documentação principal
└── requirements.txt        # Dependências do projeto (FastAPI, SQLAlchemy, etc.)
```
