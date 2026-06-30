from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import engine, create_engine, select, text
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column
from database import SessionLocal
from pydantic import BaseModel

# Inicializa o framework
app = FastAPI(title="API Centro de Referência - UESPI")

def get_db():
    db = SessionLocal()
    try:
        yield db  # entrega a sessão para a rota usar
    finally:
        db.close()  # garante o fechamento mesmo se a rota lançar erro


@app.get("/")
def home():
    return {"status" : "Página Inicial :)"}

# Rota de Health Check
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status" : "ok"}