FROM python:3.9
RUN apt-get update && apt-get install -y libldap2-dev libsasl2-dev libcrack2-dev && apt-get clean && rm -rf /var/lib/apt/lists/*
WORKDIR /srv/dicts
RUN wget https://github.com/danielmiessler/SecLists/raw/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt && cracklib-format < 10-million-password-list-top-1000000.txt | cracklib-packer dict.db
COPY requirements.txt /
RUN pip install -r /requirements.txt
WORKDIR /app
#ENV FLASK_APP=usersservice
#ENV FLASK_ENV=development
#cmd python main.py
#cmd flask run --host=0.0.0.0
#CMD waitress-serve --port 5000 --call 'usersservice:create_app'
CMD gunicorn --bind 0.0.0.0:5000 wsgi:app --access-logfile -
COPY app /app
