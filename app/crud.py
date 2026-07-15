from sqlalchemy.orm import Session
from sqlalchemy import select, func
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
def create_new_user(login: str, hash_password: str, access_level: int, db: Session):
    # Instancia o novo usuário
    user = models.Usuario(
        login=login, senha_hash=hash_password, nivel_acesso_id=access_level
    )
    # Salva no banco de dados
    db.add(user)
    db.commit()
    db.refresh(user)


# Busca um usuário com base em seu login
def search_user_by_login(db: Session, username: str):
    return db.scalars(
        select(models.Usuario).where(username == models.Usuario.login)
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


def text_search(query: str, access_level: int, db: Session):
    """
    Busca por instruções utilizando strings.
    Retorna as intruções baseado no nível de acesso do usuário.
    Utiliza um índice FULLTEXT (titulo, conteudo) para a busca.
    """
    if access_level == 1:
        return db.scalars(
            select(models.Instrucao).where(
                (models.Instrucao.titulo.match(query))
                | (models.Instrucao.conteudo.match(query)),
                models.Instrucao.ativo == True,
                models.Instrucao.nivel_acesso_id == 1,
            )
        ).all()
    else:
        return db.scalars(
            select(models.Instrucao).where(
                (models.Instrucao.titulo.match(query))
                | (models.Instrucao.conteudo.match(query)),
                models.Instrucao.ativo == True,
            )
        ).all()


# Adiciona uma nova instrução (Restrito a administradores)
def create_new_instruction(
    instruction: schemas.InstrucaoCreate, db: Session, user_id: int
):
    # Instancia nova instrução e adiciona ao banco
    new_instruction = models.Instrucao(
        titulo=instruction.titulo,
        conteudo=instruction.conteudo,
        nivel_acesso_id=instruction.nivel_acesso_id,
        url_apoio=instruction.url_apoio,
        usuario_id=user_id,
    )

    db.add(new_instruction)
    db.commit()
    db.refresh(new_instruction)


# Atualiza uma instrução (Restrito a administradores)
def update_an_instruction(
    instruction: schemas.InstrucaoCreate, db: Session, instruction_id: int, user_id: int
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

    instruction_to_be_updated.usuario_atualizou_id = user_id
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
    db.delete(topic_to_be_deleted)
    db.commit()
    return topic_to_be_deleted


# ====================================
# RELACIONAMENTO ENTRE
# ENTIDADES
# ====================================
def link_topics_to_instructions(instruction_id: int, topic_id: int, db: Session):
    """
    Vincula um tópico a uma instrução.

    Retorna um objeto do tipo InstrucaoTopico, caso existam os IDs das entidades,
    e None, caso contrário.
    """
    instruction = search_item_by_id(models.Instrucao, instruction_id, db)
    topic = search_item_by_id(models.Topico, topic_id, db)

    if not instruction or not topic:
        return None

    instruction_topic = models.InstrucaoTopico(
        instrucao_id=instruction_id, topico_id=topic_id
    )

    db.add(instruction_topic)
    db.commit()
    db.refresh(instruction_topic)
    return instruction_topic


def delete_link_topics_instructions(instruction_id: int, topic_id: int, db: Session):
    # Busca o relacionamento
    """
    Desvincula um tópico de uma instrução.

    Retorna um objeto do tipo InstrucaoTopico caso
    uma relação entre eles seja encontrada, e None, caso contrário.
    """
    instruction_topic = db.scalars(
        select(models.InstrucaoTopico).where(
            models.InstrucaoTopico.instrucao_id == instruction_id,
            models.InstrucaoTopico.topico_id == topic_id,
        )
    ).first()

    if not instruction_topic:
        return None

    db.delete(instruction_topic)
    db.commit()
    return instruction_topic


def find_instructions_by_topic(topic_id: int, db: Session, is_public: bool):
    """
    Procura instruções filtrando por tópicos.

    Caso o usuário seja anônimo, o filtro é utilizado através de tópicos públicos, retornando
    apenas instruções de acesso livre.
    Se o usuário for um servidor logado, é possível filtrar
    todas as instruções por todos os tópicos.
    """
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
    else:
        return db.scalars(
            select(models.Instrucao)
            .join(models.InstrucaoTopico)
            .join(models.Topico)
            .where(
                models.InstrucaoTopico.topico_id == topic_id,
            )
        ).all()


def link_media_to_instruction(
    media_id: int, instruction_id: int, display_order: int, db: Session
):
    """
    Anexa uma mídia existente no banco de dados a uma instrução.

    Retorna um objeto do tipo InstrucaoMidia, ou None, caso os IDs inseridos não
    existam no banco.
    """
    media = search_item_by_id(models.Midia, media_id, db)
    instruction = search_item_by_id(models.Instrucao, instruction_id, db)

    if not media or not instruction:
        return None

    media_instruction = models.InstrucaoMidia(
        instrucao_id=instruction_id, midia_id=media_id, ordem_exibicao=display_order
    )

    db.add(media_instruction)
    db.commit()
    db.refresh(media_instruction)
    return media_instruction


def delete_media_from_instruction(instruction_id: int, media_id: int, db: Session):
    """
    Deleta uma mídia de uma instrução.

    Retorna um objeto do tipo InstrucaoMidia, ou None, caso
    não exista uma relação entre a instrução e a mídia inseridas.
    """
    instruction_media = db.scalars(
        select(models.InstrucaoMidia).where(
            models.InstrucaoMidia.instrucao_id == instruction_id,
            models.InstrucaoMidia.midia_id == media_id,
        )
    ).first()

    if not instruction_media:
        return None

    db.delete(instruction_media)
    db.commit()
    return instruction_media


# ====================================
# CRUD DE MÍDIAS
# ====================================
def add_new_midia(
    file_path: str, caption: str, instruction_id: int, display_order: int, db: Session
):
    """
    Insere a nova mídia no banco e, em seguida,
    vincula-a na instrução em que está sendo utilizada.

    Retorna um objeto do tipo Midia, ou None, caso a instrução não seja encontrada.
    """
    new_media = models.Midia(caminho_arquivo=file_path, legenda=caption)

    instruction = search_item_by_id(models.Instrucao, instruction_id, db)
    if not instruction:
        return None

    db.add(new_media)
    db.commit()
    db.refresh(new_media)

    link_media_to_instruction(new_media.id, instruction_id, display_order, db)
    return new_media
