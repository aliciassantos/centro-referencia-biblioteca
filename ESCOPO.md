# Definição de Escopo e Regras de Negócio (Fase 0)

Este documento registra as decisões tomadas em conjunto com a orientação do projeto para guiar o desenvolvimento do Centro de Referência Digital da Biblioteca da UESPI.

## 1. Perfil de Usuários ("Servidores")
> **Pergunta:** Quem exatamente vai acessar o painel restrito para criar/editar instruções? Serão apenas os bibliotecários, ou bolsistas/estagiários também terão acesso?
- [ ] **Decisão:** Os bibliotecários terão acesso à parte administrativa e poderão realizar as operações CRUD nas instruções.

## 2. Políticas de Segurança e Senha
> **Pergunta:** Existe alguma regra da TI da UESPI para senhas? (Ex: mínimo de 8 caracteres, uso de caracteres especiais, obrigatoriedade de troca a cada X meses?)
- [ ] **Decisão:** Não existe um padrão definido, mas iremos adotar um para mais segurança.

## 3. Identidade Visual e Interface
> **Pergunta:** Existe algum manual de marca da UESPI ou um padrão de cores (azul/amarelo) obrigatório que a interface deve seguir? Há alguma exigência estrita de acessibilidade (como alto contraste nativo)?
- [ ] **Decisão:** Seguiremos com o padrão de cores presentes no site da UESPI, sem alta exigência de acessibilidade.

## 4. Escopo da Primeira Entrega (MVP)
> **Pergunta:** Para a nossa primeira versão de testes rodando na biblioteca, quais e quantas instruções reais precisam estar cadastradas no banco para o sistema ser considerado útil?
- [ ] **Decisão:** Pelo menos as intruções principais dos alunos (cerca de 10)

>**Pergunta:** O que precisa existir na primeira entrega? (ex: "alunos conseguem ler instruções" já é suficiente pra primeira versão, ou ele espera o CRUD completo de servidor já na v1?)
- [ ] **Decisão:** É importante que os alunos consigam ler as instruções utilizando os filtros de busca por tópico, juntamente com a barra de pesquisa

# Fundação do projeto (Fase 1)

- Criei o repositório público, com licença MIT

- Criei o .gitignore, coloquei os arquivos adequados no momento

- Criei o ambiente virtual Python (venv)

- Defini uma estrutura de pastas inicial para o projeto

- Configurei as variáveis de ambiente

- Subi uma conexão FastAPI + SQLAlchemy + MySQL local, com uma rota de "health check" para testar se está tudo ok

- Configurei o Alembic e gerei a primeira migration a partir do DDL revisado 

- Rodei a migration em um banco vazio para testar a criação

Como o uvicorn abre corretamente, exibindo a rota de health check e o banco existe criado via migration, a fase 1 está concluída.


### 📋 Mapeamento de Schemas (Pydantic) — Fase 2

Essa é a parte inicial dos schemas com o Pydantic, sujeitas a alteração no futuro

- [ ] **Módulo: Usuário e Autenticação**
  - Schema de Entrada (`UsuarioCreate`): `login`, `senha` *(com validações de tamanho/espaço)*
  - Schema de Saída (`UsuarioResponse`): `id`, `login`, `nivel_acesso_id`, `ativo`, `data_criacao`

- [ ] **Módulo: Tópicos (Categorias)**
  - Schema de Entrada (`TopicoCreate`): `nome`, `publico`
  - Schema de Saída (`TopicoResponse`): `id`, `nome`, `publico`

- [ ] **Módulo: Instruções (Rotinas)**
  - Schema de Entrada (`InstrucaoCreate`): `titulo`, `conteudo`, `nivel_acesso_id`, `url_apoio`
  - Schema de Saída (`InstrucaoResponse`): `id`, `titulo`, `conteudo`, `data_atualizacao`, `data_criacao`, `nivel_acesso_id`, `usuario_id`, `usuario_atualizou_id`, `ativo`

Inseri dados de testes em um novo arquivo (seed.py), juntamente com outro arquivo para testar as queries (testar_queries.py)
Assim, é possível, em um script solto, importar os models e fazer queries que retornam dados reais do banco.

### 📋 Autenticação e Autorização — Fase 3

- Para essa fase, criei um arquivo (security.py) para a criação e validação de senhas e tokens. As senhas são trasnformadas em hash utilizando o bcrypt, evitando salvá-las em texto puro no banco de dados

- A rota de login foi feita utilizando JWT, pois economiza o armazenamento de dados em memória

- Criei uma identificação do usuário para proteger rotas

- Adicionada uma lógica que exibe as instruções conforme o nível de acesso

- Apenas administradores conseguem criar, atualizar e deletar instruções, enquanto servidores e administradores têm acesso total à leitura.

- O visitante anônimo só consegue ler as instruções do seu nível

Agora é possível provar, testando, que um usuário sem login não acessa conteúdo restrito, e que tentar editar uma instrução sem estar logado retorna erro 403.