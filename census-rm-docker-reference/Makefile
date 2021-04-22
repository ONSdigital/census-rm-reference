up:
	docker network inspect censusrmdockerdev_reference >/dev/null || docker network create censusrmdockerdev_reference
	docker-compose -f dev.yml -f rm-services.yml up -d ${SERVICE} ;
	pipenv install --dev
	pipenv run python setup_database.py
	# ./setup_pubsub.sh
	
down:
	docker-compose -f dev.yml -f rm-services.yml down

pull:
	docker-compose -f dev.yml -f rm-services.yml pull ${SERVICE}

logs:
	docker-compose -f dev.yml -f rm-services.yml logs --follow ${SERVICE}