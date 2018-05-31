FROM python:3.6-alpine3.7

WORKDIR /app

ADD . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 80

ENV NAME Oogieboogieman

CMD ["python", "app.py"]
