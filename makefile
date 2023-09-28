create-env:
	python -m venv env

linux-set-db:
	docker compose -p cia_espirituosa down
	docker compose -p cia_espirituosa rm
	docker compose --env-file ./LBARM/.env -p cia_espirituosa up --build --force-recreate -d

set-db:
	docker-compose -p cia_espirituosa down
	docker-compose -p cia_espirituosa rm
	# unset SECRET_KEY EMAIL_HOST EMAIL_HOST_USER EMAIL_HOST_PASSWORD DEFAULT_DATABASE_USER DEFAULT_DATABASE_PASS DEFAULT_DATABASE_HOST DEFAULT_DATABASE_PORT
	docker-compose --env-file ./LBARM/.env -p cia_espirituosa up --build --force-recreate -d

reset-migration:
	./manage.py migrate prev_log zero

create-migration:
	./manage.py makemigrations

migration: create-migration
	./manage.py migrate

seed:
	./manage.py loaddata product.json
	./manage.py loaddata purchase.json
	./manage.py loaddata sale.json
	./manage.py loaddata origem.json
	./manage.py loaddata stock.json
	./manage.py loaddata open_order.json
	./manage.py loaddata basic_agreement.json
	./manage.py loaddata lbarmtipouser.json

setup: migration seed

soft-reset-db: reset-migration setup

hard-reset-db: set-db setup

linux-hard-reset-db: linux-set-db setup

superuser:
	./manage.py createsuperuser --username user --email user@email.com

test-be:
	./manage.py test

server:
	./manage.py runserver

front:
	cd ./backoffice-vue; pnpm serve
