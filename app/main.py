from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import engine, create_engine, select, text
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column
from app.database import SessionLocal, engine
from app.models import Base, Instrucao, Usuario
from pydantic import BaseModel
from app.security import (
    verify_token,
    verify_password,
    get_password_hash,
    generate_token,
)
from app.schemas import UsuarioCreate, InstrucaoCreate, InstrucaoResponse
from app import crud

# Inicializa o framework
app = FastAPI(title="API Centro de Referência - UESPI")


def get_db():
    db = SessionLocal()
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
        payload = verify_token(token)
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")
    # Busca o usuário com base no id do token, caso ele seja válido
    user = db.scalars(select(Usuario).where(Usuario.id == user_id)).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")


@app.get("/")
def home():
    return {"status": "Página Inicial :)"}


# Rota de criação de um novo usuário
@app.post("/usuarios")
def create_user(new_user: UsuarioCreate, db: Session = Depends(get_db)):
    # Gera o hash da senha de forma segura
    hash_password = get_password_hash(new_user.senha)
    # Instancia o novo usuário
    user = Usuario(login=new_user.login, senha_hash=hash_password, nivel_acesso_id=2)
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
    user = db.scalars(
        select(Usuario).where(form_data.username == Usuario.login)
    ).first()

    if user and verify_password(form_data.password, user.senha_hash):
        # Gera um novo token
        new_token = generate_token(user.id)
        # Chaves de retorno do Swagger
        return {"access_token": new_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")


# Lista as instruções de acordo com o nivel de acesso
@app.get("/instrucoes")
def show_instructions(
    db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)
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
    current_user: Usuario = Depends(get_current_user),
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
    instruction: InstrucaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    # Somente os servidores administradores podem adicionar novas instruções
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    crud.create_new_instruction(instruction, db)
    return {"status": "Instrução criada com sucesso!"}


# Rota para atualizar instrução (Restrita a servidores administradores)
@app.put("/instrucoes/{instruction_id}")
def update_instruction(
    instruction_id: int,
    instruction_form: InstrucaoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    # Somente os servidores administradores podem atualizar instruções
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Procura a instrução no banco de dados
    instruction_to_be_updated = crud.update_an_instruction(
        instruction_form, db, instruction_id
    )

    if not instruction_to_be_updated:
        raise HTTPException(status_code=404, detail="Instrução não encontrada")

    return {"status": "Instrução atualizada com sucesso!"}


# Rota para deletar instrução (Restrita a servidores administradores)
@app.delete("/instrucoes/{instruction_id}")
def delete_instruction(
    instruction_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):

    # Somente os servidores administradores podem deletar instruções
    if current_user is None or current_user.nivel_acesso_id != 3:
        raise HTTPException(status_code=403, detail="Usuário não autorizado")

    # Busca a instrução a ser deletada no banco
    instruction_to_be_deleted = crud.delete_an_instruction(instruction_id, db)

    if not instruction_to_be_deleted:
        raise HTTPException(status_code=404, detail="Instrução não encontrada")

    return {"status": "Instrução deletada com sucesso"}
