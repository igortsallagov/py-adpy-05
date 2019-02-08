import email
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

header = None


class Mail:

    def __init__(self, login, password, imap_address, smtp_address):
        self.login = login
        self.password = password
        self.imap = imap_address
        self.smtp = smtp_address

    def create_letter(self, subject, message, *args):
        recipients = args
        letter = MIMEMultipart()
        letter['From'] = self.login
        letter['To'] = ', '.join(recipients)
        letter['Subject'] = subject
        letter.attach(MIMEText(message))
        return letter

    def send_mail(self, subject, message, *args):
        letter = self.create_letter(subject, message, *args)
        mail_sender = smtplib.SMTP(self.smtp, 587)

        # identify ourselves to SMTP client
        mail_sender.ehlo()

        # secure our email with TLS encryption
        mail_sender.starttls()

        # re-identify ourselves as an encrypted connection
        mail_sender.ehlo()

        mail_sender.login(self.login, self.password)
        mail_sender.sendmail(self.login, args, letter.as_string())

        mail_sender.quit()

    def get_mail(self, header=None):
        mail_getter = imaplib.IMAP4_SSL(self.imap)
        mail_getter.login(self.login, self.password)
        mail_getter.list()
        mail_getter.select("inbox")
        criterion = '(HEADER Subject "%s")' % header if header else 'ALL'
        result, data = mail_getter.uid('search', None, criterion)
        assert data[0], 'There are no letters with current header'
        latest_email_uid = data[0].split()[-1]
        result, data = mail_getter.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_string(raw_email)
        mail_getter.logout()
        return email_message
    
