FROM python:3.7 

# Copy over requirements and install them
COPY requirements.txt /
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8050

CMD ["gunicorn","--worker-tmp-dir=/dev/shm", "--workers=2", "--threads=4", "--worker-class=gthread", "main:app"]
