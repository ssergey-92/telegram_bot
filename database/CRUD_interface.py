from typing import Any, TypeVar
from peewee import fn, SqliteDatabase, Model


T = TypeVar('T')


class CrudDb:

    @staticmethod
    def create_entries(db: SqliteDatabase, model: T, user_id: int, command) \
            -> None:
        with db.atomic():
            model.insert(user_id=user_id, command=command).execute()

    @staticmethod
    def get_data(db: SqliteDatabase, model: T, user_id: int, *required_fields) \
            -> dict:
        with db.atomic():
            query = model.select(*required_fields).where(model.user_id == user_id)
            response = query.dicts().execute()
        return response

    @staticmethod
    def update_last_user_entry(db: SqliteDatabase, model: T, user_id: int,
                               update_field: Model, new_entry: Any) -> None:
        with db.atomic():
            last_user_data_id = model.select(fn.Max(model.id)).where(
                model.user_id == user_id).scalar()
            model.update({update_field: new_entry}).where(
                model.id == last_user_data_id).execute()

