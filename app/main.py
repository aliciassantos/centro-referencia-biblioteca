from fastapi import FastAPI

# Inicializa o framework
app = FastAPI(title="API Centro de Referência - UESPI")

# Rota de Health Check
@app.get("/health")
def health_check():
    return {"status": "ok"}