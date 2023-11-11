## Telegram Bot "Global Hotel Search" ##

### Description  ###

This is telegram bot assistant for searching hotels whole over the world.
Bot provides live data from Hotels.com https://www.hotels.com/ through
provider Hotels by Api Dojo https://rapidapi.com/apidojo/api/hotels4/.

### Functions ###

There are 3 hotel search functions available:

- Top Budget hotels search.
- Top Luxury hotels search.
- Custom hotels search.

In addition to the above bot supports help navigation and search history
functions.

### Features ###

Telegram bot is:

- User friendly.
- Providing live data.
- Easy to launch.

### Libraries ###

Following libraries and Python 3.11 is used for running the Bot:

- backoff 2.2.1
- loguru 0.7.2
- mypy 1.6.1
- peewee 3.16.3
- pyTelegramBotAPI 4.14.0
- requests 2.31.0

### Getting started ###

This Bot is tested with Python 3.11.  
There is the easy way for getting started for Python package manager
for windows:

1) Download project:  
   $ git clone https://gitlab.skillbox.ru/sergei_solop/python_basic_diploma.git

2) Rename file ".env.template" to ".env" and insert your rapid API key and
   Bot token.
    1) Register and get API key from https://rapidapi.com/apidojo/api/hotels4/.
    2) Register new telegram bot and get Bot token from BotFather
       https://telegram.me/BotFather.

3) Install libraries:  
   $ pip install -r requirements.txt

4) Launch the bot:  
   Ran "main.py"

### Developer ###

This telegram bot was developed by Sergey Solop.  
Contact email for suggestions and feedbacks solop1992@mail.ru