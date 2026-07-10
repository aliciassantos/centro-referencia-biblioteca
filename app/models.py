from sqlalchemy import (
    String,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime

# MONTAGEM DE BLOCOS NATIVOS DO PYTHON (CLASSES) COM A ESTRUTURA DO MYSQL
# ENTIDADES

"""
Valores válidos de nivel_acesso.id, por convenção (não impostos pelo banco):
  1 = Discente      -> válido em: instrucao.nivel_acesso_id, usuario.nivel_acesso_id 
  2 = Servidor       -> válido em: instrucao.nivel_acesso_id, usuario.nivel_acesso_id
  3 = Administrador  -> válido em: usuario.nivel_acesso_id (NÃO deveria ser usado em instrucao.nivel_acesso_id)
"""

"""
Define quais papéis existem no sistema.
"""


class NivelAcesso(Base):
    __tablename__ = "nivel_acesso"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relação 1:N -> um nível de acesso pertence a vários usuários
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="nivel_acesso")
    instrucoes: Mapped[list["Instrucao"]] = relationship(back_populates="nivel_acesso")


"""
Gerenciamento de servidores
"""


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # ID 1 = discente | ID 2 = servidor | ID 3 = administrador
    nivel_acesso_id: Mapped[int] = mapped_column(
        ForeignKey("nivel_acesso.id"), nullable=False, default=2
    )
    ativo: Mapped[bool] = mapped_column(nullable=False, default=True)
    data_criacao: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )

    # Relacionamentos:
    # Entre nível de acesso e os usuários (1:N)
    nivel_acesso: Mapped[NivelAcesso] = relationship(back_populates="usuarios")
    # Entre um usuário que atualizou uma ou mais instruções (1:N)
    instrucoes_atualizadas: Mapped[list["Instrucao"]] = relationship(
        back_populates="atualizador", foreign_keys="Instrucao.usuario_atualizou_id"
    )
    # Entre um usuário que criou uma ou mais instruções (1:N)
    instrucoes_criadas: Mapped[list["Instrucao"]] = relationship(
        back_populates="criador", foreign_keys="Instrucao.usuario_id"
    )


"""
Categorias das instruções
"""


class Topico(Base):
    __tablename__ = "topico"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    publico: Mapped[bool] = mapped_column(default=True)
    instrucao_topico: Mapped[list["InstrucaoTopico"]] = relationship(
        back_populates="topico"
    )


"""
Conteúdo Textual das rotinas
"""


class Instrucao(Base):
    __tablename__ = "instrucao"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    data_atualizacao: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(), onupdate=func.now(), nullable=False
    )
    data_criacao: Mapped[datetime] = mapped_column(
        server_default=func.current_timestamp(), nullable=False
    )

    # Chaves estrangeiras (FKs)
    nivel_acesso_id: Mapped[int] = mapped_column(
        ForeignKey("nivel_acesso.id"), nullable=False, default=2
    )
    usuario_atualizou_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id"))
    url_apoio: Mapped[str | None] = mapped_column(String(255))
    ativo: Mapped[bool] = mapped_column(default=True)

    # Relacionamentos:
    # 1:N -> uma instrução possui um nível de acesso, que por sua vez pertence a várias instruções
    nivel_acesso: Mapped[NivelAcesso] = relationship(back_populates="instrucoes")
    # 1:N -> um usuário pode atualizar várias instruções
    atualizador: Mapped[Usuario | None] = relationship(
        back_populates="instrucoes_atualizadas", foreign_keys=[usuario_atualizou_id]
    )
    # 1:N -> um usuário pode criar várias instruções
    criador: Mapped[Usuario | None] = relationship(
        back_populates="instrucoes_criadas", foreign_keys=[usuario_id]
    )
    # 1:N -> uma instrução pode se ligar a várias InstrucaoTopico
    instrucao_topico: Mapped[list["InstrucaoTopico"]] = relationship(
        back_populates="instrucao"
    )
    instrucoes_midias: Mapped[list["InstrucaoMidia"]] = relationship(
        back_populates="instrucao"
    )


"""
Une os tópicos de uma mesma instrução
"""


class InstrucaoTopico(Base):
    __tablename__ = "instrucao_topico"

    instrucao_id: Mapped[int] = mapped_column(
        ForeignKey("instrucao.id", ondelete="CASCADE"), primary_key=True
    )
    topico_id: Mapped[int] = mapped_column(
        ForeignKey("topico.id", ondelete="CASCADE"), primary_key=True
    )

    # Relacionamentos:
    # InstrucaoTopico refere-se a uma instrução e a um topico por vez (1:N)
    instrucao: Mapped[Instrucao] = relationship(
        back_populates="instrucao_topico", foreign_keys=[instrucao_id]
    )
    topico: Mapped[Topico] = relationship(
        back_populates="instrucao_topico", foreign_keys=[topico_id]
    )


"""
Armazena arquivos de mídia
"""


class Midia(Base):
    __tablename__ = "midia"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    caminho_arquivo: Mapped[str] = mapped_column(
        String(255), nullable=True, unique=True
    )

    legenda: Mapped[str | None] = mapped_column(String(150))
    data_upload: Mapped[datetime] = mapped_column(
        nullable=False, default=func.current_timestamp()
    )

    instrucoes_midias: Mapped[list["InstrucaoMidia"]] = relationship(
        back_populates="midia"
    )


"""
Une as mídias que serão exibidas em uma instrução
"""


class InstrucaoMidia(Base):
    __tablename__ = "instrucao_midia"

    instrucao_id: Mapped[int] = mapped_column(
        ForeignKey("instrucao.id"), primary_key=True
    )
    midia_id: Mapped[int] = mapped_column(ForeignKey("midia.id"), primary_key=True)
    ordem_exibicao: Mapped[int] = mapped_column(nullable=False)
    # Relacionamentos:
    # InstrucaoMidia refere-se a uma instrução e a uma midia por vez (1:N)
    instrucao: Mapped[Instrucao] = relationship(
        back_populates="instrucoes_midias", foreign_keys=[instrucao_id]
    )
    midia: Mapped[Midia] = relationship(
        back_populates="instrucoes_midias", foreign_keys=[midia_id]
    )
