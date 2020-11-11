FROM pulumi/pulumi-python:2.13.2
RUN pip3 install wheel --upgrade
RUN mkdir -p /app
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app/
