# SACP — Sistema de Acompanhamento e Cuidado Pastoral

**A web application for managing pastoral care, follow-ups, tasks, and community engagement.**

O **SACP** é uma aplicação web desenvolvida para apoiar a organização do cuidado pastoral em comunidades cristãs. Seu propósito é centralizar informações administrativas sobre pessoas, contatos, acompanhamentos e atividades, facilitando a continuidade do cuidado e a colaboração entre responsáveis.

O sistema foi pensado para substituir controles dispersos em anotações e mensagens, sem se tornar um repositório de aconselhamentos ou informações íntimas.

> **Status:** projeto acadêmico em desenvolvimento. Os módulos principais estão implementados; relatórios, revisão de segurança, testes finais e validação de uso ainda estão em andamento. **Não indicado para uso em produção com dados reais sem essas etapas.**

## Funcionalidades

- **Pessoas e visitantes:** cadastro, consulta, edição, inativação, reativação e filtros.
- **Acompanhamentos pastorais:** registro de responsável, prioridade, situação e histórico de contatos, visitas e encaminhamentos.
- **Tarefas:** responsáveis, prazos, prioridades, conclusão, reabertura e identificação de pendências atrasadas.
- **Dashboards:** indicadores e itens que precisam de atenção; visão simplificada para a recepção.
- **Pequenos Grupos:** cadastro de grupos, líderes, participantes e histórico de vínculos.
- **Discipulados:** registro de discipulador, pessoa acompanhada e situação do vínculo.
- **Escola Bíblica Dominical (EBD):** turmas e participação das pessoas.
- **Pedidos de oração:** registro e acompanhamento com acesso restrito.
- **Usuários:** administração de contas e controle de acesso por perfil.

## Perfis de acesso

| Perfil | Permissões principais |
| --- | --- |
| **Administrador (`admin`)** | Administração do sistema, usuários e módulos. |
| **Liderança pastoral (`pastoral`)** | Gestão de acompanhamentos, tarefas, grupos, discipulados, EBD e pedidos de oração. |
| **Líder (`lider`)** | Acesso aos módulos operacionais autorizados, com consulta de grupos, discipulados e EBD. |
| **Recepção (`recepcao`)** | Cadastro e consulta de pessoas; painel inicial simplificado. |

As permissões são aplicadas nas rotas do servidor, além da apresentação condicional da interface. A política de acesso aos dados exibidos dentro de páginas compartilhadas integra a revisão final de segurança.

## Tecnologias

- **Backend:** Python, Flask e Flask-SQLAlchemy.
- **Banco de dados:** PostgreSQL.
- **Autenticação e formulários:** Flask-Login, Flask-WTF e Werkzeug.
- **Migrações:** Flask-Migrate / Alembic.
- **Frontend:** HTML, CSS, Jinja2 e JavaScript.
- **Versionamento:** Git e GitHub.

## Estrutura do projeto

```text
SACP/
├── app/
│   ├── forms/           # Formulários e validações
│   ├── models/          # Modelos e relacionamentos
│   ├── routes/          # Rotas e regras de acesso
│   ├── static/css/      # Estilos
│   ├── templates/       # Páginas HTML/Jinja2
│   ├── permissions.py   # Decorators de autorização
│   └── __init__.py      # Configuração da aplicação
├── migrations/          # Histórico de migrações do banco
├── config.py            # Configurações da aplicação
├── requirements.txt     # Dependências Python
└── run.py               # Inicialização local
```

## Executando localmente

### Pré-requisitos

- Python compatível com as dependências do projeto;
- PostgreSQL instalado e em execução;
- Git (para clonar o repositório).

### 1. Clone e configure o ambiente

```powershell
git clone <URL-DO-REPOSITORIO>
cd SACP
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Os comandos acima são para **PowerShell no Windows**. Em outros sistemas, o comando de ativação do ambiente virtual muda.

### 2. Configure o banco e as variáveis de ambiente

Crie um banco PostgreSQL e um usuário com as permissões necessárias para a aplicação.

Crie um arquivo `.env` na raiz do projeto, seguindo este exemplo:

```dotenv
DATABASE_URL=postgresql+psycopg://USUARIO:SENHA@localhost:5433/NOME_DO_BANCO
SECRET_KEY=gere-uma-chave-secreta-forte-e-unica
```

A porta `5433` corresponde à configuração utilizada no ambiente de desenvolvimento original; ajuste para a porta da sua instalação PostgreSQL.

**Não publique** o `.env`, credenciais, informações pessoais ou backups contendo dados reais. Confirme que esses arquivos estão cobertos pelo `.gitignore`.

### 3. Aplique as migrações

```powershell
python -m flask --app run.py db upgrade
```

### 4. Crie o administrador inicial

No terminal:

```powershell
python -m flask --app run.py shell
```

No console interativo:

```python
from getpass import getpass
from app import db
from app.models import Usuario

admin = Usuario(
    nome="Administrador",
    email="admin@example.com",
    perfil="admin",
    ativo=True
)
admin.definir_senha(getpass("Senha inicial: "))
db.session.add(admin)
db.session.commit()
```

Esse procedimento deve ser realizado **apenas uma vez**, em um banco recém-configurado. Use um endereço de e-mail próprio e uma senha forte; não registre a senha no repositório.

### 5. Inicie o servidor

```powershell
python run.py
```

Acesse o endereço informado pelo Flask no terminal (no ambiente local usual, `http://127.0.0.1:5000`).

## Privacidade e segurança

O SACP pode lidar com **dados pessoais sensíveis**, inclusive informações relacionadas à vida religiosa. Por isso, o projeto busca aplicar princípios de minimização, acesso por perfil e registro de informações estritamente necessárias ao acompanhamento.

- Evite registrar relatos íntimos, detalhes de aconselhamento, diagnósticos ou outras informações desnecessárias.
- Não utilize dados reais de membros e visitantes durante os testes de desenvolvimento.
- Mantenha credenciais e chaves fora do controle de versão.
- Antes de qualquer implantação, conclua a revisão de permissões, testes de segurança, configuração de ambiente, proteção de dados e política de retenção.

## Próximas etapas

- Relatórios e filtros gerenciais, com exportação de dados adequada às permissões.
- Testes funcionais integrados e revisão de regras de negócio.
- Testes de segurança (controle de acesso, IDOR, CSRF, XSS, SQL injection e sessão).
- Correções e ajustes de usabilidade e responsividade.
- Validação com usuários responsáveis pelo cuidado pastoral.
- Documentação técnica e manual de uso.

## Sobre o projeto

Projeto acadêmico de extensão na área de Engenharia de Software, voltado à aplicação prática de levantamento de requisitos, modelagem de dados, desenvolvimento web, autenticação, autorização e testes em um contexto comunitário real.

O sistema possui estrutura e terminologia genéricas, de modo que possa ser adaptado a diferentes comunidades.
