FROM python:3.6-buster

WORKDIR /usr/src/metadataset

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/metadataset/requirements.txt
RUN pip install -r requirements.txt

COPY . /usr/src/metadataset/

RUN pip install awscli
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
RUN env AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID env AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY aws s3 cp s3://metadataset-db/metadataset.$(date +%F).sql /usr/src/metadataset/db_dump

CMD python manage.py collectstatic --no-input --clear; gunicorn metadataset.wsgi:application --bind 0.0.0.0:8000
