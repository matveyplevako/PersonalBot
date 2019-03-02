import json
import imaplib
import email as emaillib
import os
from email.header import decode_header
from services.DataBase import DB

user_data = DB("USER_DATA", user_id="TEXT", email="TEXT", password="TEXT", last_uid="TEXT")
mail_services = DB("MAIL_SERVICES", email="TEXT", imap="TEXT", web_mail="TEXT")


def remove_email_from_user(user_id, email):
    user_data.delete_item(user_id=user_id, email=email)


def get_data_about_user(user_id):
    return user_data.get_items(user_id=user_id)


def get_mail_object(email, password, imap, status="UNSEEN"):
    mail = imaplib.IMAP4_SSL(imap)
    mail.login(user=email, password=password)
    mail.select("inbox")
    result, response_data = mail.uid('search', None, status)
    uids = response_data[0]

    # no unseen messages
    if len(uids) == 0:
        return mail, 0

    last_unseen_email_uid = uids.split()[-1]
    return mail, last_unseen_email_uid


def add_new_email(user_id, email, password, imap):
    user_id = str(user_id)
    try:
        mail, last_unseen_email_uid = get_mail_object(email, password, imap, status="ALL")
    except Exception as e:
        print(e)
        return False

    user_data.add_item(user_id=user_id, email=email, password=password, last_uid=last_unseen_email_uid.decode('utf-8'))
    return True


def get_new_email(email, password, last_uid):
    domain = email.split("@")[-1]
    imap, link = mail_services.get_items(email=domain)[0][1:]
    mail, last_unseen_email_uid = get_mail_object(email, password, imap)
    if int(last_unseen_email_uid) >= int(last_uid):
        result, data = mail.uid('fetch', last_unseen_email_uid, '(RFC822)')
        raw_email = data[0][1]
        email_message = emaillib.message_from_bytes(raw_email)
        sender = email_message["From"].split()[-1].replace("<", "").replace(">", "")
        subject = decode_header(email_message["Subject"])[0][0]
        if type(subject) == bytes:
            try:
                subject = subject.decode("UTF-8")
            except:
                try:
                    subject = subject.decode("koi8-r")
                except:
                    subject = ""

        return sender, subject, link


def get_domain_data(domain):
    return mail_services.get_items(email=domain)


def get_users_data():
    return user_data.get_all_rows()
