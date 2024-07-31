"""Module with ORM table 'history' and its initialization"""
import os

from peewee import (
    SqliteDatabase,
    Model,
    AutoField,
    DateTimeField,
    TextField,
    IntegerField,
)

parent_dir_abs_path = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(parent_dir_abs_path, os.getenv("DB_NAME"))
db = SqliteDatabase(db_path)


class History(Model):
    """
    Class History for history table in telegram_bot.db (SQL database).
    Parent class(peewee.Model)

    Attributes:
        id(int): self history table id with AutoField format
        user_id(int): user id
        created_at(int): creation time with DateTimeField format
        command(str): bot command
        user_request(str): details of user request
        bot_response(str): details of bot response
    """

    id = AutoField()
    user_id = IntegerField()
    created_at = DateTimeField()
    command = TextField()
    user_request = TextField(default="Search was canceled by user")
    bot_response = TextField(default="not initialized")

    class Meta:
        """
        Inner Class Meta.

        Attributes:
            database(.db): database
            table_name(str): name of table in db
        """

        database = db
        table_name = "history"


"""Create table History if it is not existed in telegram_bot.db """
with db.atomic():
    db.create_tables([History])
