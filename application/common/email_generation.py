import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import sys
from application.common.loggerfile import my_logger


def emailsender(fromaddr, toaddr, subject, message, password):
    try :
        msg = MIMEMultipart()
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Subject'] = subject
        email_body = message.split(".")
        if email_body[1] == "html":
            indexfile = open(message, "r")
            body = indexfile.read()
            msg.attach(MIMEText(body, 'html'))
            indexfile.close()
        else:
            body = message
            msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(fromaddr, password)
        text = msg.as_string()
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        my_logger.error(exc_type)
        my_logger.error(fname)
        my_logger.error(exc_tb.tb_lineno)
