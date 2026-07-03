from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func
from app.database import engine
from app.models import Usuario, Instrucao, Topico, InstrucaoTopico

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:    
    print("\n--- TESTE 1: Buscar instruções com visibilidade privada (ID = 2) ---")
    '''
    SELECT titulo, nivel_acesso_id
    FROM instrucao
    WHERE nivel_acesso_id = 2;
    '''
    instruction = db.scalars(
        select(Instrucao).where(
            Instrucao.nivel_acesso_id == 2
        )
    ).all()
    
    for i in instruction:
        print(f'Instrução: {i.titulo} | Visibilidade: privada (ID = {i.nivel_acesso_id})')

    print("\n--- TESTE 2: Criar uma busca textual ---")
    '''
    SELECT titulo, conteudo
    FROM instrucao
    WHERE titulo LIKE("%login%") OR conteudo LIKE("%login%") -- Solução não recomendada
    '''
    search = db.scalars(
        select(Instrucao).where(
                (Instrucao.titulo.like("%login%")) | 
                (Instrucao.conteudo.like("%login%"))
            )
        ).all()
    
    for s in search:
        print(f'Resultado da busca: {s.titulo} - {s.conteudo}')

    print("\n--- TESTE 3: Listar usuários e a quantidade de instruções criadas por ele ---")
    '''
    SELECT u.login, u.id, COUNT(i.usuario_id)
    FROM usuario u INNER JOIN instrucao i
    ON u.id = i.usuario_id
    GROUP BY u.id, u.login
    '''
    user_list = db.execute(
        select(
            Usuario.login, 
            Usuario.id,
            func.count(Instrucao.id)
        )
        .join(Instrucao, Usuario.id == Instrucao.usuario_id, isouter=True) # Mostra quem não tem instruções também
        .group_by(Usuario.id, Usuario.login)
    ).all()
    
    for login, id, n_instructions in user_list:
        print(f'Usuário: {login} | ID: {id} | Quantidade de instruções: {n_instructions}')


    print('\n--- TESTE 4: Descobrir quais instruções estão vinculadas ao tópico "Cadastro no Sistema" ---')
    '''
    SELECT i.titulo, i.conteudo
    FROM instrucao i INNER JOIN instrucaotopico it 
    ON i.id = it.instrucao_id
    INNER JOIN topico t 
    ON t.id = it.topico_id
    WHERE t.nome = "Cadastro no Sistema"
    '''
    target_topic = db.scalars(
        select(Topico).where(Topico.nome == "Cadastro no Sistema")
    ).first()

    if target_topic:
        print(f"Instruções vinculadas ao tópico [{target_topic.nome}]:")
        for assoc in target_topic.instrucao_topico:
            print(f" -> Título: {assoc.instrucao.titulo}")
            print(f'Conteúdo: {assoc.instrucao.conteudo}')
    else:
        print("Tópico não encontrado.")


except Exception as e:
    print(f"❌ Erro ao executar as queries: {e}")
finally:
    db.close()