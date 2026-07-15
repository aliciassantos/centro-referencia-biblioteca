from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, DataError
from app import database, models, security, schemas, crud

# Inicializa o framework
app = FastAPI(title="API Centro de Referência - UESPI")


def get_db():
    db = database.SessionLocal()
    try:
        yield db  # entrega a sessão para a rota usar
    finally:
        db.close()  # garante o fechamento mesmo se a rota lançar erro


# Define que as rotas passam a exigir um token JWT para dar acesso ao usuário
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """
    Dependência que identifica quem é o usuário atual (se houver um)

    Verifica a validade do token. Caso não haja um, o usuário possui acesso público.
    Caso haja um token, verifica-o e capta o usuário atual.
    """
    if token is None:
        return None
    try:
        payload = security.verify_token(token)
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = crud.search_item_by_id(models.Usuario, user_id, db)
    if user:
        return user
    else:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")


@app.get("/")
def home():
    return {"status": "Página Inicial :)"}


@app.post("/usuarios")
def create_user(new_user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """
    Adição de um novo usuário ao banco de dados.
    Geração de senha em hash para salvar no banco de dados de forma segura.
    """
    hash_password = security.get_password_hash(new_user.senha)
    crud.create_new_user(new_user.login, hash_password, 2, db)

    return {"status": "Usuário criado com sucesso!"}


# Rota de login
@app.post("/login")
# O form data captura o form do Swagger (O login e a senha)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # Busca o usuário pelo login digitado
    user = crud.search_user_by_login(db, form_data.username)

    if user and security.verify_password(form_data.password, user.senha_hash):
        # Gera um novo token
        new_token = security.generate_token(user.id)
        # Chaves de retorno do Swagger
        return {"access_token": new_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")


# ====================================
# ROTAS DE INSTRUÇÕES
# ====================================
@app.get(
    "/instrucoes/busca",
    response_model=list[schemas.InstrucaoResponse],
    tags=["Instruções"],
)
def get_instruction_by_text(
    q: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    """
    Realiza uma busca por instruções baseada em strings e no nível de acesso
    do usuário.
    Retorna uma lista de resultados, ou uma lista vazia, caso não encontre nenhuma instrução.
    """
    if current_user is None:
        search_result = crud.text_search(q, 1, db)
    else:
        search_result = crud.text_search(q, 3, db)

    if not search_result:
        raise HTTPException(status_code=404, detail="Nenhum resultado encontrado.")
    return search_result


@app.get("/instrucoes", tags=["Instruções"])
def show_instructions(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Lista todas as instruções. Exibe o resultado de acordo com o nível de acesso.

    Para usuários comuns, expõe apenas instruções públicas que não exigem nível de acesso.
    Para servidores, todas as instruções ativas.
    """
    if current_user is None:
        return crud.get_instruction_by_access_level(db, 1)
    return crud.get_instruction_by_access_level(db, 3)


@app.get("/instrucoes/{instruction_id}", tags=["Instruções"])
def search_a_specific_instruction(
    instruction_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Busca por uma instrução específica. Exibe o resultado de acordo com o nível de acesso.
    Uma instrução pode existir e não ser exposta a um usuário se o seu nível de acesso não permitir.
    """
    if current_user is None:
        instruction = crud.search_an_instruction(instruction_id, db, 1)
    else:
        instruction = crud.search_an_instruction(
            instruction_id, db, current_user.nivel_acesso_id
        )
    if not instruction:
        raise HTTPException(status_code=404, detail="Instrução não encontrada")
    return instruction


@app.post("/instrucoes", tags=["Instruções"])
def create_instruction(
    instruction: schemas.InstrucaoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Adiciona uma nova instrução ao banco de dados. Apenas administradores podem realizar
    essa operação.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    crud.create_new_instruction(instruction, db, current_user.id)
    return {"status": "Instrução criada com sucesso!"}


@app.put("/instrucoes/{instruction_id}", tags=["Instruções"])
def update_instruction(
    instruction_id: int,
    instruction_form: schemas.InstrucaoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Atualiza uma instrução no banco de dados. Apenas administradores podem realizar
    essa operação.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    instruction_to_be_updated = crud.update_an_instruction(
        instruction_form, db, instruction_id, current_user.id
    )

    if not instruction_to_be_updated:
        raise HTTPException(status_code=404, detail="Instrução não encontrada")

    return {"status": "Instrução atualizada com sucesso!"}


@app.delete("/instrucoes/{instruction_id}", tags=["Instruções"])
def delete_instruction(
    instruction_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Deleta uma instrução do banco de dados.
    A exclusão não remove a instrução permanentemente, apenas a torna inativa (soft delete).
    Apenas administradores podem realizar essa operação.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    instruction_to_be_deleted = crud.delete_an_instruction(instruction_id, db)

    if not instruction_to_be_deleted:
        raise HTTPException(status_code=404, detail="Instrução não encontrada")

    return {"status": "Instrução deletada com sucesso"}


# ====================================
# ROTAS DE TÓPICOS
# ====================================
@app.get("/topicos", response_model=list[schemas.TopicoResponse], tags=["Tópicos"])
def show_topics(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Listagem de tópicos baseada no nível de acesso do usuário.

    Para usuários não logados, retorna tópicos com nível de acesso público
    Para os logados, retorna todos os tópicos
    """
    if current_user == None:
        topics = crud.get_topics_by_access_level(db, True)
    else:
        topics = crud.get_topics_by_access_level(db, False)

    if not topics:
        raise HTTPException(status_code=404, detail="Nenhum tópico encontrado.")
    return topics


@app.post("/topicos", tags=["Tópicos"])
def create_topic(
    topic: schemas.TopicoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Adiciona um novo tópico ao banco de dados. Apenas administradores podem realizar
    essa operação.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    crud.create_new_topic(topic, db)
    return {"status": "Tópico criado com sucesso!"}


@app.put("/topicos/{topic_id}", tags=["Tópicos"])
def update_topic(
    topic_id: int,
    topic_form: schemas.TopicoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Atualiza um tópico do banco de dados. Apenas administradores podem realizar
    essa operação.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    topic_to_be_updated = crud.update_an_topic(topic_form, db, topic_id)

    if not topic_to_be_updated:
        raise HTTPException(status_code=404, detail="Tópico não encontrada")

    return {"status": "Tópico atualizado com sucesso!"}


@app.delete("/topicos/{topic_id}", tags=["Tópicos"])
def delete_a_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Remove um tópico do banco de dados. Apenas administradores podem realizar
    essa operação.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    topic_to_be_deleted = crud.delete_an_topic(topic_id, db)

    if not topic_to_be_deleted:
        raise HTTPException(status_code=404, detail="Tópico não encontrado")

    return {"status": "Tópico deletado com sucesso!"}


# ====================================
# ROTAS DE RELACIONAMENTO ENTRE
# ENTIDADES
# ====================================
@app.post("/instrucoes/{instruction_id}/topicos/{topic_id}", tags=["Relacionamentos"])
def link_instruction_topic(
    instruction_id: int,
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Associa um tópico a uma instrução com os IDs fornecidos.

    Apenas usuários administradores (nível 3) têm permissão para vincular.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    instruction_topic = crud.link_topics_to_instructions(instruction_id, topic_id, db)

    if instruction_topic is None:
        raise HTTPException(
            status_code=404,
            detail="Não foi possível realizar a associação: ID da instrução ou do tópico é inválido",
        )
    return {"status": "Associação realizada com sucesso!"}


@app.delete("/instrucoes/{instruction_id}/topicos/{topic_id}", tags=["Relacionamentos"])
def remove_link_instruction_topic(
    instruction_id: int,
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Remove a associação entre um tópico e uma instrução.

    Exclui o vínculo existente entre os IDs fornecidos.
    Apenas usuários administradores (nível 3) têm permissão.
    Retorna 404 caso a relação informada não seja encontrada no banco.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")
    try:
        instruction_topic = crud.delete_link_topics_instructions(
            instruction_id, topic_id, db
        )
        if not instruction_topic:
            raise HTTPException(status_code=404, detail="Relação não encontrada")
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Tópico já vinculado à instrução")
    return {"status": "Relação deletada com sucesso!"}


@app.get(
    "/topicos/{topic_id}/instrucoes",
    response_model=list[schemas.InstrucaoResponse],
    tags=["Relacionamentos"],
)
def search_instructions_by_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Busca instruções por tópico.

    Retorna a lista de instruções associadas a um tópico específico.
    Se o usuário não estiver autenticado (visitante), a busca retornará apenas
    as instruções públicas (padrão). Se estiver autenticado, retorna o conteúdo completo.
    """
    if current_user is None:
        instructions = crud.find_instructions_by_topic(topic_id, db, True)

    else:
        instructions = crud.find_instructions_by_topic(topic_id, db, False)

    if not instructions:
        raise HTTPException(
            status_code=404, detail="Nenhuma instrução encontrada para este tópico."
        )
    return instructions


@app.post("/instrucoes/{instruction_id}/midias/{media_id}", tags=["Relacionamentos"])
def link_existing_media(
    instruction_id: int,
    media_id: int,
    display_order: int = Form(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Cria um vínculo entre uma mídia existente
    e uma instrução no banco de dados.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    try:
        media_instruction = crud.link_media_to_instruction(
            media_id, instruction_id, display_order, db
        )
        # Caso não nencontre a mídia ou a instrução
        if not media_instruction:
            raise HTTPException(status_code=404, detail="Dado não encontrado.")

        return {"status": "Mídia anexada com sucesso!"}
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Mídia já vinculada à instrução.")


@app.delete("/instrucoes/{instruction_id}/midias/{media_id}", tags=["Relacionamentos"])
def delete_link_instruction_media(
    instruction_id: int,
    media_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Remove uma mídia de uma instrução.

    Acesso restrito aos administradores.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado.")

    media_instruction = crud.delete_media_from_instruction(instruction_id, media_id, db)
    if not media_instruction:
        raise HTTPException(status_code=404, detail="Mídia não vinculada à instrução.")

    return {"status": "Mídia removida com sucesso!"}


# ====================================
# ROTAS DE MÍDIA
# ====================================
@app.post(
    "/instrucoes/{instruction_id}/midias",
    response_model=schemas.MidiaResponse,
    tags=["Mídias"],
)
def upload_midia(
    instruction_id: int,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    display_order: int = Form(...),
    caption: str | None = Form(None),
    current_user: models.Usuario = Depends(get_current_user),
):
    """
    Realiza o upload de um novo arquivo de mídia (imagem, vídeo, etc.)
    e o associa diretamente a uma instrução existente no banco de dados.
    """
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    UPLOAD_DIR = Path("uploads/midias")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        while content := file.file.read(1024 * 1024):
            buffer.write(content)

    new_media = crud.add_new_midia(
        str(file_path), caption, instruction_id, display_order, db
    )
    return new_media
