FROM python:3

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN chmod 755 *

ENV TOKEN=<bot_token>

CMD ["python", "tibot.py"]