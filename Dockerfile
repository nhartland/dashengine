FROM python:3.7-alpine

RUN apk update
RUN apk add make automake gcc g++ subversion python3-dev

COPY requirements.txt /
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8050

CMD ["python", "main.py"]
