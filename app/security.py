from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv
import os
import bcrypt

# Carrega a variável de ambiente
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


# Geração de senhas em hash
def get_password_hash(password: str) -> str:
    # Limpa os espaços em branco da senha
    password_clean = password.strip()
    # Converte a senha para bytes
    password_bytes = password_clean.encode("utf-8")

    # Gera o salt e o hash
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(password_bytes, salt)

    return hash_bytes.decode("utf-8")


# Verificação de identidade
def verify_password(entry_password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(
            entry_password.encode("utf-8"), password_hash.encode("utf-8")
        )
    except:
        return False


# Geração de um token de acesso utilizando JWT
def generate_token(user_id: int) -> str:
    duration = timedelta(minutes=45)
    # "sub" -> identificação do usuário
    # "exp" -> tempo de validez do token
    payload = {"sub": str(user_id), "exp": datetime.now(timezone.utc) + duration}
    return jwt.encode(payload, key=SECRET_KEY, algorithm="HS256")


def verify_token(token: str):
    return jwt.decode(token, key=SECRET_KEY, algorithms=["HS256"])
