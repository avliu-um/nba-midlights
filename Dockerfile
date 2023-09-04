# syntax=docker/dockerfile:1
FROM python
WORKDIR /code
#COPY . .
COPY requirements.txt requirements.txt
COPY run.sh run.sh
COPY runner.py runner.py
COPY lib/chromedriver_mac64 chromedriver

RUN pip3 install --upgrade pip
RUN pip install -r requirements.txt
RUN apt update && apt install -y chromium-driver

ENTRYPOINT ["sh", "./run.sh"]
