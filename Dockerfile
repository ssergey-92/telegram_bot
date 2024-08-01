FROM python:3.10

RUN apt-get update && apt-get install -y python3-dev pip

COPY ./requirements.txt /telegram_bot/
RUN pip install -r /telegram_bot/requirements.txt

COPY ./ /telegram_bot/

WORKDIR /telegram_bot/
ENV PYTHONPATH="/telegram_bot:${PYTHONPATH}"

CMD ["python", "launch_bot.py"]