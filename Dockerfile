FROM python:3.10

COPY . .

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

CMD ["python3","app.py"]