build:
	docker build -t usersservice .

run:
	docker run -e FLASK_ENV=development -p 5000:5000 --rm -it usersservice
