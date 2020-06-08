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
import sys
import logging

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)

user_data = DB("USER_DATA", user_id="TEXT", email="TEXT", password="TEXT", last_uid="TEXT")
mail_services = DB("MAIL_SERVICES", email="TEXT", imap="TEXT", web_mail="TEXT")

login_email = {}  # key - email, value - mail object


def remove_email_from_user(user_id, email):
    user_data.delete_item(user_id=user_id, email=email)


def get_data_about_user(user_id):
    return user_data.get_items(user_id=user_id)


def login_into_email_box(email, password, imap):
    mail = imaplib.IMAP4_SSL(imap)
    try:
        mail.login(user=email, password=password)
    except Exception:
        raise
    mail.select("inbox")

    return mail


def get_last_unread_uid(mail, status="UNSEEN"):
    mail.noop()
    result, response_data = mail.uid('search', None, status)
    uids = response_data[0]

    # no unseen messages
    if len(uids) == 0:
        return -1

    last_unseen_email_uid = uids.split()[-1]
    return last_unseen_email_uid


def get_mail_object_and_last_unread_uid(email, password, imap, status="UNSEEN"):
    if email in login_email:
        mail = login_email[email]
        try:
            return mail, get_last_unread_uid(mail, status)
        except Exception as e:
            logging.error(email)
            logging.error(e)
            logging.error(traceback.format_tb(sys.exc_info()[-1]))
            del login_email[email]

    mail = login_into_email_box(email, password, imap)
    login_email[email] = mail
    logging.info(f"new login {email}")

    return mail, get_last_unread_uid(mail, status)


def add_new_email(user_id, email, password, imap):
    user_id = str(user_id)
    try:
        mail, last_unseen_email_uid = get_mail_object_and_last_unread_uid(email, password, imap, status="ALL")
        user_data.add_item(user_id=user_id, email=email, password=password,
                           last_uid=last_unseen_email_uid.decode('utf-8'))
        return True
    except Exception as e:
        logging.error(email)
        logging.error(e)
        logging.error(traceback.format_tb(sys.exc_info()[-1]))
        return False


def get_email_message(data):
    try:
        raw_email = data[0][1]
        return emaillib.message_from_bytes(raw_email)
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_tb(sys.exc_info()[-1]))
        raw_email = data[1][1]
        return emaillib.message_from_bytes(raw_email)


def get_new_email(email, password, last_uid, chat_id):
    domain = email.split("@")[-1]
    imap, link = mail_services.get_items(email=domain)[0][1:]
    mail, last_unseen_email_uid = get_mail_object_and_last_unread_uid(email, password, imap)
    if int(last_unseen_email_uid) >= int(last_uid):
        logging.debug(f"fetching email for {email} {last_unseen_email_uid}")
        result, data = mail.uid('fetch', last_unseen_email_uid, '(RFC822)')
        email_message = get_email_message(data)
        sender = email_message["From"].split()[-1].replace("<", "").replace(">", "")
        charset = "utf-8"
        prefix = None
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

            _id = int(last_unseen_email_uid)
            prefix = f"{chat_id}_{_id}"
            image_filename = f"{prefix}.png"
            html_template_filename = f"{prefix}.html"
            with open(html_template_filename, "w") as tmp:
                tmp.write(content)
            os.system(f"{os.environ['WKHTMLTOIMAGE_BIN']} {html_template_filename} {image_filename}")
            # os.remove(html_template_filename)
            compressMe(image_filename)
            link = upload_image_from_file(image_filename)
            os.remove(image_filename)
        except Exception as e:
            logging.error(email)
            logging.error(e)
            logging.error(traceback.format_tb(sys.exc_info()[-1]))
            with open('mail.pickle', 'wb') as f:
                pickle.dump(email_message, f)
            link = None

        if type(subject) == bytes:
            try:
                subject = subject.decode(charset)
            except Exception as e:
                logging.error(email)
                logging.error(e)
                logging.error(traceback.format_tb(sys.exc_info()[-1]))
                subject = ""
        return sender, subject, link, prefix


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
