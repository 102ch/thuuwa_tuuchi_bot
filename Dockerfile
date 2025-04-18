FROM python:3.10-slim as builder

RUN mkdir app

WORKDIR /app

COPY . /app

RUN apt update
RUN apt upgrade
RUN apt install -y build-essential gcc

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

FROM python:3.10-slim-buster as production

RUN mkdir app

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages/
COPY --from=builder /app /app/

CMD ["python3","app.py"]