from python:3.9
run apt-get update && apt-get install libldap2-dev libsasl2-dev && apt-get clean && rm -rf /var/lib/apt/lists/*
copy requirements.txt /
run pip install -r /requirements.txt
#ENV FLASK_APP=usersservice
#ENV FLASK_ENV=development
WORKDIR /app
#cmd python main.py
#cmd flask run --host=0.0.0.0
CMD waitress-serve --port 5000 --call 'usersservice:create_app'
copy app /app
