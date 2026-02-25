# ⛪ Sistema Shekinah PE - Gestão Eclesiástica

Um sistema completo de gestão para igrejas, projetado com uma arquitetura limpa, interface premium nativa e alta segurança de dados. Construído em Python (Flask) e PostgreSQL.

## 🚀 Tecnologias e Stack (O Motor)
- **Backend:** Python 3, Flask 3.1.2, SQLAlchemy 2.0
- **Banco de Dados:** PostgreSQL (via `psycopg2-binary`)
- **Frontend:** HTML5, CSS3, Vanilla JS, Jinja2, FontAwesome, Leaflet (Mapas), FullCalendar (Agendas)
- **Infraestrutura/Deploy:** Nginx (Proxy Reverso), Gunicorn (WSGI), Systemd (Serviço Linux)
- **Autenticação:** Flask-Login (Acesso restrito a administradores)

## 🏗️ Arquitetura do Projeto (Blueprints)
O sistema adota o padrão de "Fábrica de Aplicações" (`create_app`) e modulariza suas rotas e lógicas através do sistema de **Blueprints** do Flask:

- **`membros`**: CRUD completo com foto, tipos (Adulto/Criança/Visitante), vínculos ministeriais, congregações e exclusão segura em cascata.
- **`eventos`**: Gestão do calendário. Suporta Agendas recorrentes (cultos fixos) e Eventos temporários. Inclui sistema complexo anti-zumbi para limpeza do banco de dados ao apagar regras de agenda.
- **`grupos`**: Gestão de Ministérios e Funções (Cargos), com bloqueio de exclusão em caso de vínculos existentes para evitar erros 500 (`IntegrityError`).
- **`congregacoes`**: Controle das filiais/locais da igreja.
- **`api`**: Rotas em formato JSON para requisições assíncronas do frontend (ex: instanciar agendas, salvar listas de presença em lote).
- **`auth`**: Login e controle de sessão segura.

## 💾 Modelagem de Dados (Entity-Relationship)
As principais entidades mapeadas no banco de dados (`igreja.py`) são:
* `Membro` (Nome, Tipo, Nascimento, Batismo, Alergias, Responsaveis, Foto)
* `Congregacao` (Nome, Endereço, Status)
* `Ministerio` & `Funcao` (Cargos e Departamentos)
* `MembroMinisterio` (Tabela associativa de vínculo com dados)
* `Evento` & `Agenda` (Datas temporárias e regras de recorrência)
* `Inscricao` & `Presenca` (Listas de chamada, relógio de checkin/checkout)

## 🎨 Interface e Experiência do Usuário (UX)
* **Design Premium:** Sistema de cores sólidas e clean, sem dependência de bibliotecas CSS pesadas como Bootstrap ou Tailwind.
* **Modais Nativos:** Ações de Criação e Edição não necessitam recarregar a página.
* **Smart Flash Messages:** Notificações flutuantes (Verde/Success e Vermelho/Danger) com inteligência em Vanilla JS para auto-destruição suave após 4 segundos, sem poluir o DOM.

## 🛠️ Instalação Local (Para Desenvolvimento)
1. Clone o repositório: `git clone [url_do_seu_repo]`
2. Crie e ative o ambiente virtual: `python3 -m venv venv && source venv/bin/activate`
3. Instale as dependências: `pip install -r requirements.txt`
4. Configure suas variáveis de ambiente para conexão com o PostgreSQL.
5. Inicie a aplicação Flask.

*Documentação gerada como parte da reestruturação arquitetural do sistema. 2026.*
