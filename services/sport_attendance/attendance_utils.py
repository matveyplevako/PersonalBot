from services.DataBase import DB
from services.logger import logger
from datetime import datetime

attendance_records = DB("ATTENDANCE_RECORDS", user_id="TEXT", start="TIMESTAMPTZ", finish="TIMESTAMPTZ")


def add_attendance(user_id, start, finish):
    logger.info("logging adding")
    try:
        attendance_records.add_item(user_id=user_id, start=start, finish=finish)
    except:
        return False
    return True


def get_attendance_for_period(user_id, start, finish):
    request = f"SELECT SUM(FINISH - START) FROM ATTENDANCE_RECORDS WHERE " \
              f"USER_ID='{user_id}' AND START>='{start}' AND " \
              f"FINISH <= '{finish}'"
    td = attendance_records.excecute(request)[0][0]
    if td:
        td = td.days * 24 * 3600 + td.seconds
        return td // 3600, td // 60 % 60
    else:
        return 0, 0


def get_attendance_for_this_term(user_id):
    now = datetime.now()
    if now.month > 6:
        term_start = 7
    else:
        term_start = 1

    start = datetime(year=now.year, month=term_start, day=1)

    request = f"SELECT SUM(FINISH - START) FROM ATTENDANCE_RECORDS WHERE " \
              f"USER_ID='{user_id}' AND START>='{start}'"
    td = attendance_records.excecute(request)[0][0]
    if td:
        td = td.days * 24 * 3600 + td.seconds
        return td // 3600, td // 60 % 60
    else:
        return 0, 0
