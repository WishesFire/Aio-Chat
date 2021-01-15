FROM python:3.7.4

ADD . /serv
WORKDIR /serv
COPY requirements.txt /serv

RUN pip install -r requirements.txt

COPY . /serv

EXPOSE 8080

CMD ["python", "main.py"]