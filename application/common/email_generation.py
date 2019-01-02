import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def emailsender(fromaddr, toaddr, subject, message, password):
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
