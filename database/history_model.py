from datetime import datetime
from peewee import (SqliteDatabase, Model, AutoField, DateTimeField,
                    TextField, IntegerField)


db = SqliteDatabase('database/telegram_bot.db')


class History(Model):
    id = AutoField()
    user_id = IntegerField()
    created_at = DateTimeField(default=datetime.now())
    command = TextField()
    user_request = TextField(default='terminated')
    bot_response = TextField(default='not initialized')

    class Meta:
        database = db
        table_name = 'history'


with db.atomic():
    db.create_tables([History])





