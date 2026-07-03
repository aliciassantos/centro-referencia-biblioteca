#================================================================
# SEED DE DADOS DE TESTE
#================================================================
import sys
from datetime import datetime
from sqlalchemy.orm import sessionmaker
# Importações absolutas baseadas na estrutura do projeto
from app.database import engine
from app.models import NivelAcesso, Usuario, Topico, Instrucao, InstrucaoTopico

SessionLocal = sessionmaker(bind=engine)

def populate_database():
    db = SessionLocal()
    try:
        print("⏳ Iniciando a inserção de dados de teste (Seed)...")

        # POPULAR NÍVEIS DE ACESSO
        # Garantindo a convenção: 1=Discente, 2=Servidor, 3=Administrador
        levels = [
            NivelAcesso(id=1, nome="Discente"),
            NivelAcesso(id=2, nome="Servidor"),
            NivelAcesso(id=3, nome="Administrador")
        ]
        
        # O merge evita erros se rodar o script mais de uma vez
        for level in levels:
            db.merge(level)
        db.commit()
        print("✅ Níveis de acesso configurados (Discente, Servidor, Administrador).")

        # 2. POPULAR USUÁRIOS DE TESTE
        # Simulando hashes simples para o ambiente de testes
        users = [
            Usuario(
                id=1, 
                login="admin_biblioteca", 
                senha_hash="hash_senha_admin_123", 
                nivel_acesso_id=3, 
                ativo=True
            ),
            Usuario(
                id=2, 
                login="fatima_servidora", 
                senha_hash="hash_senha_servidor_456", 
                nivel_acesso_id=2, 
                ativo=True
            )
        ]
        for user in users:
            db.merge(user)
        db.commit()
        print("✅ Usuários de teste criados (admin_biblioteca, fatima_servidora).")

        # 3. POPULAR TÓPICOS (CATEGORIAS)
        topics = [
            Topico(id=1, nome="Devolução de Livros", publico=True),
            Topico(id=2, nome="Cadastro no Sistema", publico=True),
            Topico(id=3, nome="Manutenção Interna", publico=False) # Visível apenas internamente
        ]
        for topic in topics:
            db.merge(topic)
        db.commit()
        print("✅ Tópicos criados.")

        # 4. POPULAR INSTRUÇÕES (ROTINAS)
        instructions = [
            Instrucao(
                id=1,
                titulo="Como renovar empréstimos online",
                conteudo="1. Acesse o portal da biblioteca.\n2. Faça login com suas credenciais.\n3. Vá em 'Meus Empréstimos' e clique em 'Renovar'.",
                nivel_acesso_id=1,  # Destinado a Discentes
                usuario_id=1,       # Criado pelo Admin
                ativo=True
            ),
            Instrucao(
                id=2,
                titulo="Procedimento para inventário de acervo",
                conteudo="Instrução restrita para servidores sobre como passar o leitor de código de barras nas prateleiras setoriais.",
                nivel_acesso_id=2,  # Destinado a Servidores
                usuario_id=2,       # Criado pela Fátima
                ativo=True
            )
        ]
        for instruction in instructions:
            db.merge(instruction)
        db.commit()
        print("✅ Instruções de rotina criadas.")

        # 5. ASSOCIAR INSTRUÇÕES AOS TÓPICOS (Tabela Associativa N:N)
        associations = [
            InstrucaoTopico(instrucao_id=1, topico_id=2), # 'Renovação' vinculada a 'Cadastro'
            InstrucaoTopico(instrucao_id=2, topico_id=3)  # 'Inventário' vinculado a 'Manutenção Interna'
        ]

        for association in associations:
            db.merge(association)
        db.commit()
        print("✅ Associações de Tópicos e Instruções vinculadas com sucesso.")

        print("\n🚀 BANCO DE DADOS POPULADO COM SUCESSO!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Erro ao popular o banco de dados: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()