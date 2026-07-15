# 🏛️ Centro de Referência Digital — Biblioteca UESPI
> **Documento de Escopo, Regras de Negócio e Registro de Desenvolvimento**

Este documento registra as decisões tomadas em conjunto com a orientação do projeto e o histórico de implementação para guiar o desenvolvimento do sistema.

---

## 📋 Fase 0: Definição de Escopo e Regras de Negócio

### 👥 1. Perfil de Usuários ("Servidores")
* **Pergunta:** Quem exatamente vai acessar o painel restrito para criar/editar instruções? Serão apenas os bibliotecários, ou bolsistas/estagiários também terão acesso?
* [x] **Decisão:** Os bibliotecários terão acesso à parte administrativa e poderão realizar as operações CRUD nas instruções.

### 🔒 2. Políticas de Segurança e Senha
* **Pergunta:** Existe alguma regra da TI da UESPI para senhas?
* [x] **Decisão:** Não existe um padrão definido pela instituição, mas adotaremos requisitos mínimos de segurança (tamanho e caracteres especiais) no sistema.

### 🎨 3. Identidade Visual e Interface
* **Pergunta:** Existe algum manual de marca da UESPI ou um padrão de cores obrigatório? Há exigência de acessibilidade estrita?
* [x] **Decisão:** Seguiremos com a paleta de cores oficial do site da UESPI (Azul e Amarelo), sem requisitos estritos de alta acessibilidade nesta fase.

### 🚀 4. Escopo da Primeira Entrega (MVP)
* **Pergunta:** Quantas instruções reais precisam estar cadastradas para o sistema ser considerado útil?
* [x] **Decisão:** Pelo menos as instruções principais voltadas para os alunos (aproximadamente 10 rotinas cadastradas).
* **Pergunta:** O que precisa existir na primeira entrega?
* [x] **Decisão:** É essencial que os alunos consigam ler as instruções utilizando filtros de busca por tópico e a barra de pesquisa geral.

---

## 🛠️ Fase 1: Fundação do Projeto
* [x] **Repositório:** Criado repositório público com a licença MIT.
* [x] **Configuração Inicial:** Arquivo `.gitignore` configurado e ambiente virtual (`venv`) ativo.
* [x] **Estrutura de Pastas:** Arquitetura do projeto padronizada e variáveis de ambiente configuradas.
* [x] **Banco de Dados:** Conexão estabelecida usando FastAPI + SQLAlchemy + MySQL local com rota de *health check* ativa.
* [x] **Migrações:** Alembic configurado; primeira migração gerada a partir do DDL revisado e aplicada com sucesso.

---

## 📐 Fase 2: Mapeamento de Schemas (Pydantic)
* [x] **Módulo: Usuário e Autenticação**
  * Schema de Entrada (`UsuarioCreate`): `login`, `senha` *(com validações de tamanho/espaço)*.
  * Schema de Saída (`UsuarioResponse`): `id`, `login`, `nivel_acesso_id`, `ativo`, `data_criacao`.
* [x] **Módulo: Tópicos (Categorias)**
  * Schema de Entrada (`TopicoCreate`): `nome`, `publico`.
  * Schema de Saída (`TopicoResponse`): `id`, `nome`, `publico`.
* [x] **Módulo: Instruções (Rotinas)**
  * Schema de Entrada (`InstrucaoCreate`): `titulo`, `conteudo`, `nivel_acesso_id`, `url_apoio`.
  * Schema de Saída (`InstrucaoResponse`): `id`, `titulo`, `conteudo`, `data_atualizacao`, `data_criacao`, `nivel_acesso_id`, `usuario_id`, `usuario_atualizou_id`, `ativo`.
* [x] **Massa de Testes:** Criação do script de semente (`seed.py`) e script de teste de queries (`testar_queries.py`) para validar operações com dados reais do banco.

---

## 🔑 Fase 3: Autenticação e Autorização
* [x] **Segurança (`security.py`):** Criptografia de senhas com `bcrypt` (evitando texto puro no banco) e geração/validação de tokens JWT.
* [x] **Controle de Fluxo:** Implementada a identificação do usuário logado para proteção de rotas privadas.
* [x] **Níveis de Acesso:**
  * **Administradores:** Controle total (criar, atualizar e deletar).
  * **Servidores:** Acesso total à leitura e gerenciamento básico.
  * **Visitantes anônimos:** Conseguem ler apenas instruções públicas (Nível de acesso 1).
  * *Validação realizada:* Tentativas de edições não autorizadas retornam corretamente erro `403 Forbidden`.

---

## 💾 Fase 4: CRUD de Instruções e Relacionamentos
Implementação das rotas e lógica de persistência no arquivo `crud.py` com exposição dos endpoints na `main.py`.

### 📌 Endpoints de Instruções
| Método | Endpoint | Descrição | Restrição |
| :--- | :--- | :--- | :--- |
| `GET` | `/instrucoes` | Lista instruções respeitando o nível de acesso | Livre |
| `GET` | `/instrucoes/{id}` | Busca os detalhes de uma instrução específica | Livre |
| `POST` | `/instrucoes` | Cria uma nova instrução | Apenas Admin |
| `PUT` | `/instrucoes/{id}` | Atualiza os dados de uma instrução | Apenas Admin |
| `DELETE`| `/instrucoes/{id}` | Desativa logicamente uma instrução (`ativo=False`) | Apenas Admin |
| `GET` | `/instrucoes/busca` | Realiza busca *full-text* (`MATCH...AGAINST`) por título/conteúdo | Livre |

### 🏷️ Endpoints de Tópicos (Categorias)
| Método | Endpoint | Descrição | Restrição |
| :--- | :--- | :--- | :--- |
| `GET` | `/topicos` | Lista tópicos ativos | Livre |
| `POST` | `/topicos` | Cria um novo tópico | Servidor / Admin |
| `PUT` | `/topicos/{id}` | Edita as informações de um tópico | Servidor / Admin |
| `DELETE`| `/topicos/{id}` | Remove um tópico (desvinculando-o das instruções) | Servidor / Admin |
| `GET` | `/topicos/{id}/instrucoes` | Lista todas as instruções vinculadas a um tópico | Livre |

### 🔗 Endpoints de Relacionamentos e Mídias
| Método | Endpoint | Descrição | Restrição |
| :--- | :--- | :--- | :--- |
| `POST` | `/instrucoes/{ins_id}/topicos/{top_id}` | Associa um tópico a uma instrução | Servidor / Admin |
| `DELETE`| `/instrucoes/{ins_id}/topicos/{top_id}` | Remove o vínculo entre tópico e instrução | Servidor / Admin |
| `POST` | `/instrucoes/{ins_id}/midias/{mid_id}` | Vincula uma mídia existente a uma instrução | Servidor / Admin |
| `DELETE`| `/instrucoes/{ins_id}/midias/{mid_id}` | Remove a mídia de uma instrução (com *Cascade*) | Servidor / Admin |
| `POST` | `/instrucoes/{ins_id}/midias` | Faz o upload de uma nova mídia para a instrução | Servidor / Admin |

* [x] **Tratamento de Erros:** Exceções HTTP e checagem de integridade adicionadas para garantir respostas limpas (como `404 Not Found` para registros ausentes).