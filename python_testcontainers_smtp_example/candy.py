import logging
from dataclasses import dataclass

from python_testcontainers_smtp_example.mail_util import send

ALARM_CANDY = "No more candy!!!"
MAIL_MESSAGE_BODY = "Oh no! No more candy..."

logger = logging.getLogger(__name__)


@dataclass
class ConfEmail:
    enable_send_email: bool
    host: str
    port: int
    from_addr: str
    to_addrs: list[str]


class Dashboard:
    """
    Dashboard is generic class responsible to notify final user or have a FrontEnd to show the problems.
    I choose dashboard name because it is a pretty common name for this purpose.
    In this case dashboard send an email in case there is no more candy.
    """

    def __init__(self, conf_email: ConfEmail) -> None:
        self.__allarms = []
        self.__conf_email = conf_email

    def alarm_no_candy(self):
        self.__allarms.append(ALARM_CANDY)
        if self.__conf_email.enable_send_email:
            try:
                logger.info("%s Sending email!!", ALARM_CANDY)
                send(
                    host=self.__conf_email.host,
                    port=self.__conf_email.port,
                    from_addr=self.__conf_email.from_addr,
                    to_addrs=",".join(self.__conf_email.to_addrs),
                    subject=ALARM_CANDY,
                    msg_body=MAIL_MESSAGE_BODY,
                )
            except Exception:
                logger.exception("An error occurred in sending email for NO more candy")

    def get_all_alarms(self):
        return self.__allarms


class CandyBox:
    """
    CandyBox is responsable to control and expose a, no surprise, candy box.
    So expose API to eat one (someone get one and eat it), and also notify
    dashboard in case that there is no more candy.
    """

    def __init__(self, dashboard: Dashboard, number_candy: int) -> None:
        self.__dashboard = dashboard
        self.__number_candy = number_candy

    def has_more_candy(self) -> bool:
        return self.__number_candy > 0

    def eat_one(self) -> None:
        if self.has_more_candy():
            self.__number_candy -= 1
        else:
            self.__dashboard.alarm_no_candy()

    def remaining_candy(self) -> int:
        return self.__number_candy
