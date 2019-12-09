FROM tiangolo/uwsgi-nginx-flask:python3.7

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

COPY . /app
