import logging
import smtplib
from email.mime.text import MIMEText
from email.header import Header


logger = logging.getLogger(__name__)


def send_email(receivers, content, subject='纳税平台账号确认', sender_name='纳税平台', sender_addr='', mail_host='tzcpa.com', mail_user='', mail_pass=''):
    smtp_obj = smtplib.SMTP()
    smtp_obj.connect(mail_host, 25)
    smtp_obj.login(mail_user, mail_pass)
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = Header(sender_name, 'utf-8')
    message['To'] = Header(receivers.keys()[0], 'utf-8')
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtp_obj.sendmail(sender_addr, receivers, message.as_string())
    except Exception as e:
        logger.critical(
            f'sender {sender_addr}, receivers {receivers}, message: {message}',
            exc_info=e)
