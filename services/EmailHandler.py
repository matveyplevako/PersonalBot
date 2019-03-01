import json
import imaplib
import email as emaillib
from email.header import decode_header

debug = False

USER_DATA_PATH = "services/userdata.json"
MAIL_SERVICES_PATH = "services/mail_services.json"

if debug:
    USER_DATA_PATH = "userdata.json"
    MAIL_SERVICES_PATH = "mail_services.json"


def dump_new_data(key, new_entry):
    data = get_users_data()
    data[key] = new_entry
    with open(USER_DATA_PATH, "w") as file:
        json.dump(data, file)


def remove_email_from_user(user_uid, email):
    user_uid = str(user_uid)
    data = get_data_about_user(user_uid)
    if email not in data:
        return False
    del data[email]
    dump_new_data(user_uid, data)
    return True


def get_users_data():
    with open(USER_DATA_PATH) as file:
        return json.load(file)


def get_data_about_user(user_uid):
    data = get_users_data()
    return data[str(user_uid)]


def get_mail_object(email, password, status="UNSEEN"):
    with open(MAIL_SERVICES_PATH) as serv:
        json_data = json.load(serv)
    host = json_data[email.split("@")[-1]]["imap"]
    mail = imaplib.IMAP4_SSL(host)
    mail.login(user=email, password=password)
    mail.select("inbox")
    result, response_data = mail.uid('search', None, status)
    uids = response_data[0]

    # no unseen messages
    if len(uids) == 0:
        return mail, 0

    last_unseen_email_uid = uids.split()[-1]
    return mail, last_unseen_email_uid


def add_new_email(user_id, email, password):
    user_id = str(user_id)
    data = {}
    try:
        data = get_data_about_user(user_id)
    except:
        pass
    try:
        mail, last_unseen_email_uid = get_mail_object(email, password, status="ALL")
    except:
        return False

    dump_new_data(user_id, {**data, email: {"password": password, "last_uid": int(last_unseen_email_uid)}})
    return True


def get_new_email(email, password, last_uid):
    mail, last_unseen_email_uid = get_mail_object(email, password)
    if int(last_unseen_email_uid) >= last_uid:
        result, data = mail.uid('fetch', last_unseen_email_uid, '(RFC822)')
        raw_email = data[0][1]
        email_message = emaillib.message_from_bytes(raw_email)
        sender = email_message["From"].split()[-1].replace("<", "").replace(">", "")
        subject = decode_header(email_message["Subject"])[0][0]
        if type(subject) == bytes:
            try:
                subject = subject.decode("UTF-8")
            except:
                pass
            try:
                subject = subject.decode("koi8-r")
            except:
                pass
        with open(MAIL_SERVICES_PATH) as serv:
            link = json.load(serv)[email.split("@")[-1]]["web mail"]
        return sender, subject, link


def get_known_domains():
    with open(MAIL_SERVICES_PATH) as serv:
        data = json.load(serv)
    return data.keys()
