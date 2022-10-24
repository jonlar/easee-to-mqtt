FROM python:3.8-alpine

RUN pip3 install paho-mqtt pyeasee python-dateutil

ADD *.py /app/

ENTRYPOINT ["python3", "/app/main.py"]