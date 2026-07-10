from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models, schemas, database


# ====================================
# FUNÇÕES AUXILIARES
# ====================================
# Busca por id
def search_item_by_id(entity: type, id: int, db: Session):
    return db.scalars(select(entity).where(entity.id == id)).first()


# ====================================
# CRUD DE USUÁRIO
# ====================================
# Busca um usuário com base em seu login
def search_user_by_login(db: Session, form_data: str):
    return db.scalars(
        select(models.Usuario).where(form_data.username == models.Usuario.login)
    ).first()


# ====================================
# CRUD DE INSTRUÇÕES
# ====================================
# Busca por instruções de acordo com o nível de acesso
def get_instruction_by_access_level(db: Session, level_access_id: int):
    # Retorna as instruções ativas visíveis aos discentes
    if level_access_id == 1:
        return db.scalars(
            select(models.Instrucao).where(
                (models.Instrucao.nivel_acesso_id == level_access_id),
                (models.Instrucao.ativo == True),
            )
        ).all()

    # Retorna todas as instruções ativas visíveis (Para servidores e administradores)
    else:
        return db.scalars(
            select(models.Instrucao).where(models.Instrucao.ativo == True)
        ).all()


# Adiciona uma nova instrução (Restrito a administradores)
def create_new_instruction(instruction: schemas.InstrucaoCreate, db: Session):
    # Instancia nova instrução e adiciona ao banco
    new_instruction = models.Instrucao(
        titulo=instruction.titulo,
        conteudo=instruction.conteudo,
        nivel_acesso_id=instruction.nivel_acesso_id,
        url_apoio=instruction.url_apoio,
    )

    db.add(new_instruction)
    db.commit()
    db.refresh(new_instruction)


# Atualiza uma instrução (Restrito a administradores)
def update_an_instruction(
    instruction: schemas.InstrucaoCreate, db: Session, instruction_id: int
):
    # Procura a instrução no banco de dados
    instruction_to_be_updated = search_item_by_id(models.Instrucao, instruction_id, db)

    if not instruction_to_be_updated:
        return None

    # Transforma o formulário em dicionário, trazendo apenas o que foi preenchido
    update_data = instruction.model_dump(exclude_unset=True)
    # Atualiza os campos do objeto no banco
    for key, value in update_data.items():
        setattr(instruction_to_be_updated, key, value)

    db.commit()
    db.refresh(instruction_to_be_updated)
    return instruction_to_be_updated


# Remove uma instrução (Restrito a administradores)
def delete_an_instruction(instruction_id: int, db: Session):
    # Busca a instrução a ser deletada no banco
    instruction_to_be_deleted = search_item_by_id(models.Instrucao, instruction_id, db)
    if not instruction_to_be_deleted:
        return None

    instruction_to_be_deleted.ativo = False
    # Remove a instrução e salva as alterações
    db.commit()
    return instruction_to_be_deleted


# Busca por uma instrução específica filtrada por nível de acesso
def search_an_instruction(instruction_id: int, db: Session, level_access_id: int):

    # Exibe somente as instruções que o usuário anônimo pode visualizar
    if level_access_id == 1:
        instruction = db.scalars(
            select(models.Instrucao).where(
                models.Instrucao.id == instruction_id,
                models.Instrucao.nivel_acesso_id == 1,
                models.Instrucao.ativo == True,
            )
        ).first()

        if not instruction:
            return None
        return instruction

    else:
        instruction = search_item_by_id(models.Instrucao, instruction_id, db)
        # Garante que só retorna se ela estiver ativa
        if instruction and instruction.ativo:
            return instruction
        return None


# ====================================
# CRUD DE TÓPICOS
# ====================================
# Lista todos os tópicos (De acordo com o nível de acesso)
def get_topics_by_access_level(db: Session, access_level: bool):
    # Se for público, retorna somente os visíveis a usuários sem login
    if access_level == True:
        topics = db.scalars(
            select(models.Topico).where(models.Topico.publico == access_level)
        ).all()

    else:
        # Se não for público (servidor), retorna todos os tópicos
        topics = db.scalars(select(models.Topico)).all()
    return topics


# Adiciona um novo tópico (Restrito a administradores)
def create_new_topic(topic: schemas.TopicoCreate, db: Session):
    # Instancia novo Tópico e adiciona ao banco
    new_topic = models.Topico(nome=topic.nome, publico=topic.publico)

    db.add(new_topic)
    db.commit()
    db.refresh(new_topic)


# Atualiza um tópico (Restrito a administradores)
def update_an_topic(topic: schemas.TopicoCreate, db: Session, topic_id: int):
    # Procura o tópico no banco de dados
    topic_to_be_updated = search_item_by_id(models.Topico, topic_id, db)

    if not topic_to_be_updated:
        return None

    # Transforma o formulário em dicionário, trazendo apenas o que foi preenchido
    update_data = topic.model_dump(exclude_unset=True)
    # Atualiza os campos do objeto no banco
    for key, value in update_data.items():
        setattr(topic_to_be_updated, key, value)

    db.commit()
    db.refresh(topic_to_be_updated)
    return topic_to_be_updated


# Remove um tópico (Restrito a administradores)
def delete_an_topic(topic_id: int, db: Session):
    # Busca o tópico a ser deletado no banco
    topic_to_be_deleted = search_item_by_id(models.Topico, topic_id, db)
    if not topic_to_be_deleted:
        return None

    # Remove o tópico e salva as alterações
    db.commit()
    return topic_to_be_deleted


# ====================================
# RELACIONAMENTO ENTRE
# ENTIDADES
# ====================================
# Relaciona um tópico a uma instrução
def link_topics_to_instructions(instruction_id: int, topic_id: int, db: Session):
    # Instancia o novo relacionamento
    instruction_topic = models.InstrucaoTopico(
        instrucao_id=instruction_id, topico_id=topic_id
    )

    db.add(instruction_topic)
    db.commit()
    db.refresh(instruction_topic)


# Remove o relacionamento entre um tópico e uma instrução
def delete_link_topics_instructions(instruction_id: int, topic_id: int, db: Session):
    # Busca o relacionamento
    instruction_topic = db.scalars(
        select(models.InstrucaoTopico).where(
            models.InstrucaoTopico.instrucao_id == instruction_id,
            models.InstrucaoTopico.topico_id == topic_id,
        )
    ).first()

    if not instruction_topic:
        return None
    # Remove a instrução e salva as alterações
    db.delete(instruction_topic)
    db.commit()


# Procura instruções filtrando por tópicos
def find_instructions_by_topic(topic_id: int, db: Session, is_public: bool):
    # Exibe as instruções de tópicos públicos
    if is_public is True:
        return db.scalars(
            select(models.Instrucao)
            .join(models.InstrucaoTopico)
            .join(models.Topico)
            .where(
                models.InstrucaoTopico.topico_id == topic_id,
                models.Topico.publico == is_public,
            )
        ).all()
    # Exibe todos os tópicos e, consequentemente, todas as instruções
    else:
        return db.scalars(
            select(models.Instrucao)
            .join(models.InstrucaoTopico)
            .join(models.Topico)
            .where(
                models.InstrucaoTopico.topico_id == topic_id,
            )
        ).all()
