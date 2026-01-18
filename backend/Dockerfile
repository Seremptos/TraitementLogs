FROM python:3.12-alpine

RUN apk add --update --no-cache python3 py3-pip gcc musl-dev python3-dev libffi-dev openssl-dev

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN chmod +x run.sh

EXPOSE 5000

CMD ["./run.sh"]