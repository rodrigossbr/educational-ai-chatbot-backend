
## Ativando o ambiente virtual
````shell
  source .venv/Scripts/activate
````

## Subindo o banco de dados

Para subir o container do banco
```shell
  docker compose -f ./educational-ai-chatbot-db/docker-compose.yml up -d
```

## Gerando e executando migrations

Para gerar as migrations
```shell
  python manage.py makemigrations educhatbot
```
Para executar as migrations no banco
```shell
  python manage.py migrate
```
Para listar migrations executadas
```shell
  python manage.py showmigrations educhatbot 
```
Para fazer rollbak de uma migation
```shell
  python manage.py migrate educhatbot <0001_cod>
```
Para fazer roolbak de todas as migrations
```shell
  python manage.py migrate educhatbot zero
```
Para criar um usuário inicial para o admin
```shell
  python manage.py createsuperuser
```

## Rodando a aplicação

Instalando os pacotes
```shell
  .venv/Scripts/python.exe -m pip -V
  .venv/Scripts/python.exe -m pip install --upgrade pip
  .venv/Scripts/python.exe -m pip install -r requirements.txt
```

Para atualizar o requirements 
```shell
pip freeze > requirements.txt
```

Confirmar instalação do Django
```shell
  .venv/Scripts/python.exe -m pip show django
  .venv/Scripts/python.exe -c "import sys, django; print(sys.executable); print(django.get_version())"
```

Para subir a aplicação
```shell
  .venv/Scripts/python.exe manage.py runserver 8000
```
