from services.DataBase import DB
from datetime import datetime
from services.logger import logger

attendance_records = DB("ATTENDANCE_RECORDS", user_id="TEXT", start="TIMESTAMPTZ", finish="TIMESTAMPTZ")


def add_attendance(user_id, start, finish):
    logger.info("logging adding")
    attendance_records.add_item(user_id=user_id, start=start, finish=finish)
