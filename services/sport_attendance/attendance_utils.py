from services.DataBase import DB
from services.logger import logger

attendance_records = DB("ATTENDANCE_RECORDS", user_id="TEXT", start="TIMESTAMPTZ", finish="TIMESTAMPTZ")


def add_attendance(user_id, start, finish):
    logger.info("logging adding")
    try:
        attendance_records.add_item(user_id=user_id, start=start, finish=finish)
    except:
        return False
    return True
