from typing import Any, TypeVar
from datetime import datetime
from peewee import fn, SqliteDatabase, Model

T = TypeVar('T')


class CrudDb:
    """
    Class CrudDb.
    Class for creating, reading, inserting and deleting entries for History table
    telegram bot db.
    """

    @staticmethod
    def create_entries(db: SqliteDatabase, model: T, user_id: int,
                       command: str) -> None:
        """
        Making new entry in History table.

        :param db: SqliteDatabase
        :type db: .db
        :param model: table
        :type model: class History(Model)
        :param user_id: user id
        :type user_id: int
        :param command: command shortcut
        :type command: str
        """

        with db.atomic():
            created_at = datetime.now()
            model.insert(user_id=user_id, command=command,
                         created_at=created_at).execute()

    @staticmethod
    def get_user_data(db: SqliteDatabase, model: T, user_id: int, limit: int,
                      *required_fields: Model) -> dict:
        """
        Obtaining user data from History table.

        :param db: SqliteDatabase
        :type db: .db
        :param model: table
        :type model: class History(Model)
        :param user_id: user id
        :type user_id: int
        :param limit: number of entries to get
        :type limit: int
        :param *required_fields: names of fields
        :type *required_fields: Model
        """

        with db.atomic():
            query = model.select(*required_fields).where(
                model.user_id == user_id).order_by(model.id.desc()).limit(limit)
            response = query.dicts().execute()
        return response

    @staticmethod
    def update_last_user_entry(db: SqliteDatabase, model: T, user_id: int,
                               update_field: Model, new_entry: Any) -> None:
        """
        Updating last user entry in History table.

        :param db: SqliteDatabase
        :type db: .db
        :param model: table
        :type model: class History(Model)
        :param user_id: user id
        :type user_id: int
        :param update_field: field to be updated
        :type update_field: Model
        :param new_entry: new data
        :type new_entry: Any
        """

        with db.atomic():
            last_user_data_id = model.select(fn.Max(model.id)).where(
                model.user_id == user_id).scalar()
            model.update({update_field: new_entry}).where(
                model.id == last_user_data_id).execute()
