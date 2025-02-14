FROM python:3-bookworm

WORKDIR /usr/src/app

RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]
