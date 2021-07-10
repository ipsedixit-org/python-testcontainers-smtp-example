import abc
import logging
import re
import socket
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import requests

logger = logging.getLogger(__name__)

STATUS_CODE_OK = 200
STATUS_CODE_NO_CONTENT = 204
TIMEOUT_API_SECONDS = 10


@dataclass
class MockSmtpConf:
    host: str
    smtp_port: int
    api_port: int


@dataclass
class Mail:
    from_addr: str
    to_addrs: list[str]
    received: str
    when: datetime
    subject: str
    body: str


class SMTPCommand(Enum):
    RCPT_TO = "RCPT TO"
    EHLO = "EHLO"
    MAIL_FROM = "MAIL FROM"
    DATA = "DATA"
    RSET = "RSET"
    VRFY = "VRFY"
    NOOP = "NOOP"
    QUIT = "QUIT"


class SMTPStatusCode(Enum):
    OK_200 = 200
    SYSTEM_STATUS_211 = 211
    HELP_214 = 214
    SERVICE_READY = 220
    SERVICE_CLOSING_CHANNEL_221 = 221
    ACTION_COMPLETE_250 = 250
    USER_NOT_LOCAL_251 = 251
    UNKNOW_USER_252 = 252
    START_MAIL_INPUT_354 = 354
    SERVICE_NOT_AVAILABLE_421 = 421
    REQUESTED_MAIL_ACTION_NOT_TAKEN_450 = 450
    REQUESTED_ACTION_ABORTED_451 = 451
    REQUESTED_ACTION_NOT_TAKEN_452 = 452
    SYNTAX_ERROR_500 = 500
    SYNTAX_ERROR_IN_PARAMETERS_OR_ARGUMENTS_501 = 501
    COMMAND_NOT_IMPLEMENTED_502 = 502
    BAD_SEQUENCE_OF_COMMANDS_503 = 503
    COMMAND_PARAMETER_NOT_IMPLEMENTED_504 = 504
    DOES_NOT_ACCEPT_MAIL_521 = 521
    ACCESS_DENIED_530 = 530
    REQUESTED_ACTION_NOT_TAKEN_550 = 550
    USER_NOT_LOCAL_551 = 551
    REQUESTED_MAIL_ACTION_ABORTED_552 = 552
    REQUESTED_ACTION_NOT_TAKEN_553 = 553
    TRANSACTION_FAILED_554 = 554


class SMTPCondition(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_dict(self):
        pass


class SMTPMatchAllCondition:
    def to_dict(self):
        return {"operator": "matchAll"}


class SMTPMatchContains:
    def __init__(self, matching_value) -> None:
        self._matching_value = matching_value

    def to_dict(self):
        return {"operator": "contains", "matchingValue": self._matching_value}


@dataclass
class SMTPBehaviour:
    command: SMTPCommand
    condition: SMTPCondition
    response: SMTPStatusCode


class MockSmtp:
    def __init__(self, conf: MockSmtpConf) -> None:
        self.__conf = conf

    def is_ready(self) -> bool:
        def check_conn(conn_type: str, port: int):
            s = socket.socket()
            try:
                logger.debug("Check Mock SMTP container conn_type: %s - conf: %s", conn_type, self.__conf)
                s.connect((self.__conf.host, port))
                logger.info("Mock SMTP container conn_type: %s is ready", conn_type)
                return True
            except Exception as e:
                logger.info("Mock SMTP container conn_type: %s is not ready yet - e: %s", conn_type, str(e))
                return False
            finally:
                s.close()

        return check_conn("smtp", self.__conf.smtp_port) and check_conn("api", self.__conf.api_port)

    def _mail_url(self) -> str:
        return f"http://{self.__conf.host}:{self.__conf.api_port}/smtpMails"

    def _behaviors_url(self) -> str:
        return f"http://{self.__conf.host}:{self.__conf.api_port}/smtpBehaviors"

    def clean_up(self) -> None:
        def clean_up_single_end_point(request_type, url):
            logger.debug("Try to delete %s ", request_type)
            r = requests.delete(url, timeout=TIMEOUT_API_SECONDS)
            logger.debug("Delete %s - response code: %s - text: %s", request_type, r.status_code, r.text)
            if r.status_code != STATUS_CODE_NO_CONTENT:
                raise Exception("An error occurred in clean up {}".format(request_type))

        clean_up_single_end_point(request_type="mail", url=self._mail_url())
        clean_up_single_end_point(request_type="behaviors", url=self._behaviors_url())

    def _get_mail(self, response) -> Mail:
        to_addrs = [recipient["address"] for recipient in response["recipients"]]

        grouped = re.search(r"Received:([^;]+);\r\n([^\r]+)\r\nSubject:([^\r]+)\r\n\r\n(.+)\r$", response["message"])
        if grouped is None:
            raise Exception("An error occurred in split in groups mail string {}".format(response["message"]))

        # Example: input string to convert Sat, 29 May 2021 05:11:31 +0000 (UTC)
        when = datetime.strptime(grouped.group(2).strip(), "%a, %d %b %Y %H:%M:%S %z (%Z)")

        return Mail(
            from_addr=response["from"],
            to_addrs=to_addrs,
            received=grouped.group(1).strip(),
            when=when,
            subject=grouped.group(3).strip(),
            body=grouped.group(4),
        )

    def get_mails(self) -> list[Mail]:
        logger.debug("Try to retrieve all mails")
        response = requests.get(self._mail_url(), timeout=TIMEOUT_API_SECONDS)
        logger.debug("Get all mails - response code: %s - text: %s", response.status_code, response.text)
        if response.status_code != STATUS_CODE_OK:
            raise Exception("An error occurred in get all mails")

        json_response = response.json()
        return [self._get_mail(response) for response in json_response]

    def set_behaviours(self, behaviours: list[SMTPBehaviour]) -> None:

        data = []
        for behaviour in behaviours:
            data.append(
                {
                    "command": behaviour.command.value,
                    "condition": behaviour.condition.to_dict(),
                    "response": {"code": behaviour.response.value, "message": "Fake server error"},
                }
            )

        logger.debug("Try to set behaviours %s", behaviours)
        import json

        headers = {"Content-Type": "application/json"}
        response = requests.put(
            self._behaviors_url(), data=json.dumps(data), headers=headers, timeout=TIMEOUT_API_SECONDS
        )
        logger.debug("Set behaviour - response code: %s - text: %s", response.status_code, response.text)
        if response.status_code != STATUS_CODE_NO_CONTENT:
            raise Exception("An error occurred in set behaviours")
