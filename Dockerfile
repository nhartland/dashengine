FROM python:3.10 

# Copy over requirements and install them
COPY requirements.txt /
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 8050

CMD ["sh", "start.sh"]
