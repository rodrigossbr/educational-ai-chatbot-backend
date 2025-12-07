
# Educational AI Chatbot - Backend

Este é o projeto **Backend (API REST)** do Chatbot Educacional Inclusivo. Desenvolvido em **Django**, ele utiliza padrões de arquitetura em camadas (Services/Repositories) para orquestrar a lógica entre o usuário, o banco de dados e as integrações externas (Gemini AI e Mockoon).

> **Projeto de TCC - Ciência da Computação (UNISINOS)**
> **Aluno:** Rodrigo Silveira dos Santos
> **Orientador:** Prof. Dr. Mateus Raeder

## Estrutura do Projeto

O projeto segue uma organização modular para separar responsabilidades:

```plaintext
educational-ai-chatbot-backend/
│
├── apimock/                   # Configurações e dados simulados (Mockoon)
├── config/                    # Configurações principais do projeto Django (settings.py)
├── educational-ai-chatbot-db/ # Configuração Docker do Banco de Dados
│
├── educhatbot/                # Aplicação Principal
│   ├── controllers/           # Camada de controle (Views/ViewSets)
│   ├── core/                  # Utilitários, constantes e classes base
│   ├── models/                # Definição das entidades do banco
│   ├── repositories/          # Camada de acesso a dados (Abstração do ORM)
│   ├── serializers/           # Transformação de dados (DTOs/DRF)
│   ├── services/              # Regras de negócio (Integração Gemini, Lógica de Chat)
│   └── migrations/            # Histórico de versões do banco de dados
│
├── .env                       # Variáveis de ambiente (NÃO COMITAR)
├── .env-sample                # Exemplo das variáveis necessárias
├── requirements.txt           # Dependências do projeto
└── manage.py                  # CLI do Django

## Ativando o ambiente virtual
````shell
  source .venv/Scripts/activate
````

## Tecnologias Utilizadas

* **Linguagem:** Python 3.10+
* **Framework:** Django & Django REST Framework
* **Banco de Dados:** PostgreSQL (via Docker)
* **IA Generativa:** Google Gemini API
* **Simulação** [Mockoon](https://mockoon.com/) (para APIs institucionais)

## Guia de Configuração e Execução

1. Ativando o ambiente virtual

Certifique-se de ter o Python instalado. Utilize o comando abaixo para ativar o ambiente virtual:

````shell
source .venv/Scripts/activate
````

2. Configuração de Variáveis de Ambiente (.env)

Copie o arquivo .env-sample para um novo arquivo chamado .env na raiz do projeto e preencha com suas chaves:
````shell
# Exemplo de configuração
# Configurações Django
DJANGO_SETTINGS_MODULE=config.settings
PYTHONUNBUFFERED=1
DEBUG=True

# Configurações de Log/gRPC
GRPC_VERBOSITY=NONE
GRPC_PYTHON_LOG_LEVEL=CRITICAL
GRPC_TRACE=

# Configuração LLM (Gemini)
LLM_PROVIDER=gemini
# Insira sua chave API do Google AI Studio aqui
GEMINI_API_KEY=sua_chave_secreta_aqui
GEMINI_MODEL=gemini-2.5-flash

# APIs Externas (Mockoon)
EXTERNAL_API_BASE=http://localhost:3001/api
EXTERNAL_TIMEOUT_SECS=6
EXTERNAL_RETRY_TOTAL=3
````

3. Instalando dependências

Com o ambiente ativado, instale os pacotes necessários:
````shell
# Verificar versão do pip
.venv/Scripts/python.exe -m pip -V

# Atualizar o pip
.venv/Scripts/python.exe -m pip install --upgrade pip

# Instalar requisitos do projeto
.venv/Scripts/python.exe -m pip install -r requirements.txt
````

    **Nota:** Para atualizar o arquivo requirements.txt no futuro, use:

````shell
pip freeze > requirements.txt
````

4. Subindo o banco de dados (Docker)

Para subir o container do banco de dados PostgreSQL:
````shell
docker compose -f ./educational-ai-chatbot-db/docker-compose.yml up -d
````

5. Gerando e executando migrations

````shell
# Gerar as migrations (baseado nos models)
python manage.py makemigrations educhatbot

# Executar as migrations no banco
python manage.py migrate

# Listar migrations executadas
python manage.py showmigrations educhatbot 

# (Opcional) Fazer rollback de uma migration específica
python manage.py migrate educhatbot <0001_cod>

# (Opcional) Fazer rollback de todas as migrations
python manage.py migrate educhatbot zero
````

6. Criar Usuário Admin

Para acessar o painel administrativo do Django (/admin):

````shell
python manage.py createsuperuser
````

7. Rodando a aplicação

Confirmar instalação do Django (Opcional):

````shell
.venv/Scripts/python.exe -m pip show django
.venv/Scripts/python.exe -c "import sys, django; print(sys.executable); print(django.get_version())"
````

Para subir a aplicação na porta 8000:
````shell
.venv/Scripts/python.exe manage.py runserver 8000
````
