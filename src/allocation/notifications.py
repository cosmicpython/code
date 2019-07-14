#pylint: disable=too-few-public-methods
import abc
import smtplib


class Notifications(abc.ABC):

    @abc.abstractmethod
    def send(self, destination, message):
        raise NotImplementedError


class EmailNotifications(Notifications):

    def __init__(self, smtp_host):
        self.server = smtplib.SMTP(smtp_host)
        self.server.noop()

    def send(self, destination, message):
        msg = 'Subject: allocation service notification\n{message}'
        self.server.sendmail('allocations@example.com', to_addrs=[destination], msg=msg)
