"""Module with CRUD for ORM table 'history'"""

from datetime import datetime
from typing import Any, Optional

from peewee import Model

from .history_model import db, History
from project_logging.bot_logger import bot_logger


class HistoryCRUD:
    """
    Class HistoryCRUD.
    Class with CRUD operations for ORM table 'history'.
    """

    @staticmethod
    def create_entry(user_id: int, command: str) -> int:
        """Create new entry in history table.

        Args:
            user_id (int): user id
            command (str): command shortcut

        """
        with db.atomic():
            created_at = datetime.now()
            history_id = History.insert(
                user_id=user_id, command=command, created_at=created_at,
            ).execute()
        bot_logger.debug(f"{user_id=}, {history_id=}")
        return history_id

    @staticmethod
    def get_latest_user_entries(
            user_id: int, limit: int,
    ) -> list[Optional[dict]]:
        """Get latest user records from history table as per limit.

        Args:
            user_id (int): user id
            limit (int): number of entries to get

        Returns:
            list[dict]: latest user history entries

        """
        with db.atomic():
            query = (
                History.select()
                .where(History.user_id == user_id)
                .order_by(History.id.desc())
                .limit(limit)
            )
            response = query.dicts().execute()
        bot_logger.debug(f"{user_id=}, {limit=}, {response=}")
        return response

    @staticmethod
    def update_field_by_id(
        history_id: int, update_field: Model, new_value: Any,
    ) -> None:
        """Update field in History table by history id.

        Args:
             history_id (int): history id
             update_field (Model): field to update
             new_value (Any): new value

        """
        bot_logger.debug(f"{history_id=}, {update_field=}, {new_value=}")
        with ((db.atomic())):
            (
                History.update({update_field: new_value})
                .where(History.id == history_id)
                .execute()
             )
