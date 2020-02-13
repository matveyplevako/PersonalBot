import imaplib
import email as emaillib
from email.header import decode_header
from services.DataBase import DB
from imgurpython import ImgurClient
from PIL import Image
import os
import re
import pickle
import traceback
import threading
from multiprocessing import Process, Queue
import logging

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

user_data = DB("USER_DATA", user_id="TEXT", email="TEXT", password="TEXT", last_uid="TEXT")
mail_services = DB("MAIL_SERVICES", email="TEXT", imap="TEXT", web_mail="TEXT")

lock = threading.Lock()


def remove_email_from_user(user_id, email):
    user_data.delete_item(user_id=user_id, email=email)


def get_data_about_user(user_id):
    return user_data.get_items(user_id=user_id)


def get_mail_object(email, password, imap, status="UNSEEN"):
    mail = imaplib.IMAP4_SSL(imap)
    try:
        mail.login(user=email, password=password)
    except:
        raise EOFError
    mail.select("inbox")

    with lock:
        result, response_data = mail.uid('search', None, status)
    uids = response_data[0]

    # no unseen messages
    if len(uids) == 0:
        return mail, -1

    last_unseen_email_uid = uids.split()[-1]
    return mail, last_unseen_email_uid


def add_new_email(user_id, email, password, imap):
    user_id = str(user_id)
    try:
        mail, last_unseen_email_uid = get_mail_object(email, password, imap, status="ALL")
        user_data.add_item(user_id=user_id, email=email, password=password,
                           last_uid=last_unseen_email_uid.decode('utf-8'))
        mail.logout()
        return True
    except Exception as e:
        print(e)
        return False


def get_new_email(email, password, last_uid, chat_id):
    domain = email.split("@")[-1]
    imap, link = mail_services.get_items(email=domain)[0][1:]
    mail, last_unseen_email_uid = get_mail_object(email, password, imap)
    if int(last_unseen_email_uid) >= int(last_uid):
        result, data = mail.uid('fetch', last_unseen_email_uid, '(RFC822)')
        raw_email = data[0][1]
        email_message = emaillib.message_from_bytes(raw_email)
        sender = email_message["From"].split()[-1].replace("<", "").replace(">", "")
        charset = "utf-8"
        if email_message["Subject"] is not None:
            subject = decode_header(email_message["Subject"])[0][0]
        else:
            subject = "Empty subject"
        try:
            content = None
            charset = None

            if email_message.is_multipart():
                for part in email_message.walk():
                    ctype = part.get_content_type()
                    cdispo = str(part.get('Content-Disposition'))

                    if ctype == 'text/html' and 'attachment' not in cdispo:
                        content = part.get_payload(decode=True)
                        charset = part.get_charsets()[0]
                        break

                    if ctype == 'text/plain' and 'attachment' not in cdispo:
                        content = part.get_payload(decode=True)
                        charset = part.get_charsets()[0]
            else:
                content = email_message.get_payload(decode=True)
                charset = email_message.get_charsets()[0]

            if charset is None:
                charset = 'utf-8'

            content = content.decode(charset)
            if len(re.findall("<meta.+?charset=.+?>", content)) > 0:
                content = re.sub(r"(<meta.+?charset=\"?).+?([\"> ])", r'\1utf-8\2', content)
            else:
                content = f'<head><meta http-equiv="Content-Type" content="text/\r\nhtml; charset=utf-8"/>' + content

            filename = f"{chat_id}.png"
            save_as_html(content)
            os.system(f"{os.environ['WKHTMLTOIMAGE_BIN']} temp.html {filename}")
            os.remove("temp.html")
            compressMe(filename)
            link = upload_image_from_file(filename)
            os.remove(filename)
        except:
            with open('mail.pickle', 'wb') as f:
                pickle.dump(email_message, f)
            traceback.print_exc()
            link = None

        if type(subject) == bytes:
            try:
                subject = subject.decode(charset)
            except:
                subject = ""
        return sender, subject, link


def save_as_html(source):
    with open("temp.html", "w") as tmp:
        tmp.write(source)


def upload_image_from_file(filename):
    client_id = os.environ.get("IMGUR_API_ID")
    client_secret = os.environ.get("IMGUR_API_SECRET")
    client = ImgurClient(client_id, client_secret)
    response = client.upload_from_path(filename, anon=True)
    link = response['link']
    return link


def get_domain_data(domain):
    return mail_services.get_items(email=domain)


def get_users_data():
    return user_data.get_all_rows()


def compressMe(filename):
    while os.path.getsize(filename) / 1e6 > 10:
        filename = os.path.join(os.getcwd(), filename)
        picture = Image.open(filename).convert("RGB")
        picture.save(filename, "JPEG", optimize=True)
