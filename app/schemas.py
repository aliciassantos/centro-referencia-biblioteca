from datetime import datetime
from sqlalchemy import create_engine, String, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from pydantic import BaseModel, ConfigDict, Field, field_validator


# - [ ] **Módulo: Usuário e Autenticação**
#   - Schema de Entrada (`UsuarioCreate`): `login`, `senha` *(com validações de tamanho/espaço)*
class UsuarioCreate(BaseModel):
    login: str = Field(max_length=50)
    # A senha inserida será convertida em hash posteriormente
    senha: str = Field(min_length=8)

    @field_validator("login")
    @classmethod
    def verifica_corretude_login(cls, v: str) -> str:
        if " " in v:
            raise ValueError("O login não pode conter espaços em branco.")
        return v


#   - Schema de Saída (`UsuarioResponse`): `id`, `login`, `nivel_acesso_id`,
# `ativo`, `data_criacao`
class UsuarioResponse(BaseModel):
    id: int
    login: str
    nivel_acesso_id: int
    ativo: bool
    data_criacao: datetime

    model_config = ConfigDict(from_attributes=True)


# - [ ] **Módulo: Tópicos (Categorias)**
#   - Schema de Entrada (`TopicoCreate`): `nome`, `publico`
class TopicoCreate(BaseModel):
    nome: str = Field(max_length=100)
    publico: bool


#   - Schema de Saída (`TopicoResponse`): `id`, `nome`, `publico`
class TopicoResponse(BaseModel):
    id: int
    nome: str
    publico: bool

    model_config = ConfigDict(from_attributes=True)


# - [ ] **Módulo: Instruções (Rotinas)**
#   - Schema de Entrada (`InstrucaoCreate`): `titulo`, `conteudo`,
#   `nivel_acesso_id`, `url_apoio`
class InstrucaoCreate(BaseModel):
    titulo: str = Field(max_length=255)
    conteudo: str
    nivel_acesso_id: int
    url_apoio: str | None = None


#   - Schema de Saída (`InstrucaoResponse`): `id`, `titulo`, `conteudo`, `data_atualizacao`,
#  `data_criacao`, `nivel_acesso_id`, `usuario_id`, `usuario_atualizou_id`, `ativo`
class InstrucaoResponse(BaseModel):
    id: int
    titulo: str
    conteudo: str
    data_atualizacao: datetime
    data_criacao: datetime
    nivel_acesso_id: int | None
    usuario_id: int | None
    usuario_atualizou_id: int | None
    ativo: bool

    model_config = ConfigDict(from_attributes=True)
