from sqlalchemy import Column, Integer, String, Boolean
from database import Base

# MONTAGEM DE BLOCOS NATIVOS DO PYTHON (CLASSES) COM A ESTRUTURA DO MYSQL
# ENTIDADES
class Topico(Base):
    __tablename__ = "topico"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    publico = Column(Boolean, default=True)

class Usuario(Base):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True, index=True) 
    login = Column(String(50), unique=True, nullable=False)
    senha_hash = Column(String(255), unique=False, nullable=False)


# TABELAS ASSOCIATIVAS
