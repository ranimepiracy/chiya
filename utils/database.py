import logging
import os

import dataset
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

log = logging.getLogger(__name__)


class Database:
    def __init__(self) -> None:
        self.host = os.getenv("MYSQL_HOST")
        self.db = os.getenv("MYSQL_DATABASE")
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.url = f"mysql://{self.user}:{self.password}@{self.host}/{self.db}"

    def get(self) -> dataset.Database:
        """ Returns the dataset database object. """
        return dataset.connect(url=self.url)

    def setup(self) -> None:
        """Sets up the tables needed for Chiya."""
        # Create the database if it doesn't already exist.
        engine = create_engine(self.url)
        if not database_exists(engine.url):
            create_database(engine.url)

        # Open a connection to the database.
        db = self.get()

        # Create mod_logs table and columns to store moderator actions.
        if "mod_logs" not in db:
            mod_logs = db.create_table("mod_logs")
            mod_logs.create_column("user_id", db.types.bigint)
            mod_logs.create_column("mod_id", db.types.bigint)
            mod_logs.create_column("timestamp", db.types.bigint)
            mod_logs.create_column("reason", db.types.text)
            mod_logs.create_column("type", db.types.text)
            log.info("Created missing table: mod_logs")

        # Create remind_me table and columns to store remind_me messages.
        if "remind_me" not in db:
            remind_me = db.create_table("remind_me")
            remind_me.create_column("reminder_location", db.types.bigint)
            remind_me.create_column("author_id", db.types.bigint)
            remind_me.create_column("date_to_remind", db.types.bigint)
            remind_me.create_column("message", db.types.text)
            remind_me.create_column("sent", db.types.boolean, default=False)
            log.info("Created missing table: remind_me")

        # Create timed_mod_actions table and columns to store timed moderator actions.
        if "timed_mod_actions" not in db:
            timed_mod_actions = db.create_table("timed_mod_actions")
            timed_mod_actions.create_column("user_id", db.types.bigint)
            timed_mod_actions.create_column("mod_id", db.types.bigint)
            timed_mod_actions.create_column("action_type", db.types.text)
            timed_mod_actions.create_column("start_time", db.types.bigint)
            timed_mod_actions.create_column("end_time", db.types.bigint)
            timed_mod_actions.create_column("is_done", db.types.boolean, default=False)
            timed_mod_actions.create_column("reason", db.types.text)
            log.info("Created missing table: timed_mod_actions")

        # Create ticket table and columns to store the ticket status information.
        if "tickets" not in db:
            tickets = db.create_table("tickets")
            tickets.create_column("user_id", db.types.bigint)
            tickets.create_column("status", db.types.text)
            tickets.create_column("guild", db.types.bigint)
            tickets.create_column("timestamp", db.types.bigint)
            tickets.create_column("ticket_topic", db.types.text)
            tickets.create_column("log_url", db.types.text)
            log.info("Created missing table: tickets")

        # Create settings table and columns to store key:value pairs.
        if "settings" not in db:
            settings = db.create_table("settings")
            settings.create_column("name", db.types.text)
            settings.create_column("value", db.types.text)
            settings.create_column("censored", db.types.boolean)
            log.info("Created missing table: settings")
        
        if "message_logs" not in db:
            message_logs = db.create_table("message_logs")
            message_logs.create_column("message_id", db.types.bigint)
            message_logs.create_column("author_id", db.types.bigint)
            message_logs.create_column("channel_id", db.types.bigint)
            message_logs.create_column("guild_id", db.types.bigint)
            message_logs.create_column("created_at", db.types.float)
            message_logs.create_column("content", db.types.text)
            message_logs.create_column("attachments", db.types.text)
            message_logs.create_column("is_edited", db.types.boolean)
            log.info("Created missing table: message_logs")
            

        # Commit the changes to the database and close the connection.
        db.commit()
        db.close()
