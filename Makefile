clean:
	find . -name "*.pyc" -exec rm -rf {} \;

run: clean
	docker-compose up

debug: clean
	docker-compose up -d db && docker-compose run --service-ports --rm api python src/manage.py runserver 0.0.0.0:8000

migrate: clean
	docker-compose run --rm api python src/manage.py migrate

migrations: clean
	docker-compose run --rm api python src/manage.py makemigrations

exclude_migrations: clean
	# rm */**/migrations/*[0-9]*.py
	find . -name '*[0-9]*.py' -type f -delete

install:
	pip install -r requirements.txt

user: clean
	docker-compose run --rm api python src/manage.py createsuperuser

shell: clean
	docker-compose run --rm api python src/manage.py shell

build: clean
	docker-compose build
