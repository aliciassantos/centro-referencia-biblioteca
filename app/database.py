import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Monta a URL de conexão no formato mysql+driver://usuario:senha@servidor/banco_de_dados
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Cria a Engine que abre a conexão com o MySQL na porta 3306
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cria sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria a Classe para mapear as tabelas no Python
Base = declarative_base()