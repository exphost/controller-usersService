FROM python:3.9
RUN apt-get update && apt-get install -y libldap2-dev libsasl2-dev && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /
RUN pip install -r /requirements.txt
#ENV FLASK_APP=usersservice
#ENV FLASK_ENV=development
WORKDIR /app
#cmd python main.py
#cmd flask run --host=0.0.0.0
#CMD waitress-serve --port 5000 --call 'usersservice:create_app'
CMD gunicorn --bind 0.0.0.0:5000 wsgi:app --access-logfile -
COPY app /app
