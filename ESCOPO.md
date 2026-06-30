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

- Para a fase 1 ainda configurar o Alembic e gerar a primeira migration a partir do DDL revisado e rodar a migration do zero em um banco vazio para confirmar que cria tudo corretamente