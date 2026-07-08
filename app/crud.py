from sqlalchemy.orm import Session
from sqlalchemy import select
from app import models, schemas, database


# Função auxiliar de busca por id
def search_item_by_id(entity: type, id: int, db: Session):
    return db.scalars(select(entity).where(entity.id == id)).first()


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


# Adiciona uma nova instrução (Restrita a administradores)
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
