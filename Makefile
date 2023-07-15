SHELL = /bin/bash
install:
	sudo apt update && sudo apt install sqlite3
	python -m venv venv && source ./venv/bin/activate && pip install -r requirements.txt

checkmigrations:
	python manage.py makemigrations --check --no-input --dry-run

setup:
	python manage.py makemigrations
	python manage.py migrate
	python manage.py createsuperuser

dump:
	python manage.py dumpdata quickstart -o tutorial/apps/quickstart/fixtures/quickstart.json
	python manage.py dumpdata snippets -o tutorial/apps/snippets/fixtures/snippets.json

load:
	python manage.py loaddata tutorial/apps/quickstart/fixtures/quickstart.json --app quickstart
	python manage.py loaddata tutorial/apps/snippets/fixtures/snippets.json --app snippets

serve:
	python manage.py migrate
	python manage.py runserver
