FROM python:3.9

COPY requirements.txt /app/requirements.txt

RUN python -m pip install -r /app/requirements.txt

COPY . /app

WORKDIR /app

RUN chmod 755 *

ENV TOKEN=<bot_token>

CMD ["python", "tibot.py"]

