from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from pathlib import Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
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


# Dependência que tranca as rotas restritas aos servidores
def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    # Verifica a validade do token
    # Se não tiver token, é um usuário comum (discente)
    if token is None:
        return None
    try:
        payload = security.verify_token(token)
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
    # Busca o usuário com base no id do token, caso ele seja válido
    user = crud.search_item_by_id(models.Usuario, user_id, db)
    if user:
        return user
    else:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")


@app.get("/")
def home():
    return {"status": "Página Inicial :)"}


# Rota de criação de um novo usuário
@app.post("/usuarios")
def create_user(new_user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Gera o hash da senha de forma segura
    hash_password = security.get_password_hash(new_user.senha)
    # Instancia o novo usuário
    user = models.Usuario(
        login=new_user.login, senha_hash=hash_password, nivel_acesso_id=2
    )
    # Salva no banco de dados
    db.add(user)
    db.commit()

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
# Lista as instruções de acordo com o nivel de acesso
@app.get("/instrucoes")
def show_instructions(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    if current_user == None:
        # Para usuários comuns, retorna instruções de acesso livre
        return crud.get_instruction_by_access_level(db, 1)
    # Para servidores, retorna todas as instruções
    return crud.get_instruction_by_access_level(db, 3)


# Busca por uma instrução específica
@app.get("/instrucoes/{instruction_id}")
def search_a_specific_instruction(
    instruction_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    # Se for visitante anônimo, passa o nível 1
    if current_user == None:
        instruction = crud.search_an_instruction(instruction_id, db, 1)
    # Se estiver logado, passa o nível do usuário
    else:
        instruction = crud.search_an_instruction(
            instruction_id, db, current_user.nivel_acesso_id
        )
    if not instruction:
        raise HTTPException(status_code=404, detail="Instrução não encontrada")
    return instruction


# Rota para criar nova instrução (Restrita a servidores administradores)
@app.post("/instrucoes")
def create_instruction(
    instruction: schemas.InstrucaoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    # Somente os servidores administradores podem adicionar novas instruções
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    crud.create_new_instruction(instruction, db, current_user.id)
    return {"status": "Instrução criada com sucesso!"}


# Rota para atualizar instrução (Restrita a servidores administradores)
@app.put("/instrucoes/{instruction_id}")
def update_instruction(
    instruction_id: int,
    instruction_form: schemas.InstrucaoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    # Somente os servidores administradores podem atualizar instruções
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Procura a instrução no banco de dados
    instruction_to_be_updated = crud.update_an_instruction(
        instruction_form, db, instruction_id, current_user.id
    )

    if not instruction_to_be_updated:
        raise HTTPException(status_code=404, detail="Instrução não encontrada")

    return {"status": "Instrução atualizada com sucesso!"}


# Rota para deletar instrução (Restrita a servidores administradores)
@app.delete("/instrucoes/{instruction_id}")
def delete_instruction(
    instruction_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):

    # Somente os servidores administradores podem deletar instruções
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Busca a instrução a ser deletada no banco
    instruction_to_be_deleted = crud.delete_an_instruction(instruction_id, db)

    if not instruction_to_be_deleted:
        raise HTTPException(status_code=404, detail="Instrução não encontrada")

    return {"status": "Instrução deletada com sucesso"}


# ====================================
# ROTAS DE TÓPICOS
# ====================================
# Listagem de tópicos existentes
@app.get("/topicos", response_model=list[schemas.TopicoResponse])
def show_topics(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    if current_user == None:
        # Para usuários comuns, retorna instruções de acesso livre
        topics = crud.get_topics_by_access_level(db, True)
    else:
        # Para servidores, retorna todas as instruções
        topics = crud.get_topics_by_access_level(db, False)

    if not topics:
        raise HTTPException(status_code=404, detail="Nenhum tópico encontrado.")
    return topics


# Rota para criar novo Tópico (Restrita a servidores administradores)
@app.post("/topicos")
def create_topic(
    topic: schemas.TopicoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):

    # Somente os servidores administradores podem adicionar novos tópicos
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    crud.create_new_topic(topic, db)
    return {"status": "Tópico criado com sucesso!"}


@app.put("/topicos/{topic_id}")
def update_topic(
    topic_id: int,
    topic_form: schemas.TopicoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    # Somente os servidores administradores podem atualizar tópicos
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Procura o tópico no banco de dados
    topic_to_be_updated = crud.update_an_topic(topic_form, db, topic_id)

    if not topic_to_be_updated:
        raise HTTPException(status_code=404, detail="Tópico não encontrada")

    return {"status": "Tópico atualizado com sucesso!"}


@app.delete("/topicos/{topic_id}")
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):

    # Somente os servidores administradores podem deletar tópicos
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Busca o tópico a ser deletado no banco
    topic_to_be_deleted = crud.delete_an_topic(topic_id, db)

    if not topic_to_be_deleted:
        raise HTTPException(status_code=404, detail="Tópico não encontrado")

    return {"status": "Tópico deletado com sucesso!"}


# ====================================
# ROTAS DE RELACIONAMENTO ENTRE
# ENTIDADES
# ====================================
# Cria um vínculo de um tópico a uma instrução
@app.post("/instrucoes/{instruction_id}/topicos/{topic_id}")
def link_entities(
    instruction_id: int,
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    # Somente os servidores administradores podem vincular topicos a instruções
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    crud.link_topics_to_instructions(instruction_id, topic_id, db)
    return {"status": "Associação realizada com sucesso!"}


# Deleta um vínculo entre um tópico e uma instrução
@app.delete("/instrucoes/{instruction_id}/topicos/{topic_id}")
def remove_link_entities(
    instruction_id: int,
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):

    # Somente os servidores administradores podem vincular topicos a instruções
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Remove a relação
    instruction_topic = crud.delete_link_topics_instructions(
        instruction_id, topic_id, db
    )

    if not instruction_topic:
        raise HTTPException(status_code=404, detail="Relação não encontrada")

    return {"status": "Relação deletada com sucesso!"}


# Busca instruções com base em um tópico
@app.get(
    "/topicos/{topic_id}/instrucoes", response_model=list[schemas.InstrucaoResponse]
)
def search_instructions_by_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user),
):
    if current_user is None:
        return crud.find_instructions_by_topic(topic_id, db, True)

    return crud.find_instructions_by_topic(topic_id, db, False)


# Ainda em desenvolvimento
# @app.post("/instrucoes/{instruction_id}/midias")
# def upload_midia(
#     instruction_id: int,
#     db: Session = Depends(get_db),
#     file: UploadFile = File(...),
#     ordem_exibicao: int = Form(...),
#     legenda: str = Form(None) | None,
#     current_user: models.Usuario = Depends(get_current_user),
# ):
#     # Define o caminho da pasta onde as mídias vão ficar
#     UPLOAD_DIR = Path("uploads/midias")
#     # Cria a pasta e todas as pastas pai se elas não existirem
#     UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

#     # Salva o arquivo com o nome original dele
#     file_path = UPLOAD_DIR / file.filename

#     # Copia o conteúdo do arquivo recebido para o destino
#     with open(file_path, "wb") as buffer:
#         while content := file.file.read(1024 * 1024):
#             buffer.write(content)
