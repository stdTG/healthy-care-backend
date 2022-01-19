from core.config import get_app_config
from core.utils.aws import get_ses


class Email(object):
    def __init__(self, to, subject):
        self.to = to
        self.subject = subject
        self._html = None
        self._text = None
        self._format = 'html'
        self.cfg = get_app_config()

    def html(self, html):
        self._html = html

    def text(self, text):
        self._text = text

    def send(self, from_addr=None):
        body = self._html

        if isinstance(self.to, str):
            self.to = [self.to]
        if not from_addr:
            from_addr = self.cfg.SENDER_EMAIL
        if not self._html and not self._text:
            raise Exception('You must provide a text or html body.')
        if not self._html:
            self._format = 'text'
            body = self._text

        ses_client = get_ses()

        return ses_client.send_email(
            Source=from_addr,
            Destination={
                'BccAddresses': [],
                'CcAddresses': [],
                'ToAddresses': self.to,
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': 'UTF-8',
                        'Data': self._html,
                    },
                    'Text': {
                        'Charset': 'UTF-8',
                        'Data': self._text,
                    },
                },
                'Subject': {
                    'Charset': 'UTF-8',
                    'Data': self.subject,
                },
            },
        )
