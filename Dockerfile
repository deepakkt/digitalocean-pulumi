FROM pulumi/pulumi-python:2.13.2
RUN mkdir -p /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/
WORKDIR /app
