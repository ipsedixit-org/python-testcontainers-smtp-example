import logging
import pathlib
import time

import pytest
from testcontainers.compose import DockerCompose

from python_testcontainers_smtp_example.candy import CandyBox, ConfEmail, Dashboard
from tests_integration.mock_smtp import (
    Mail,
    MockSmtp,
    MockSmtpConf,
    SMTPBehaviour,
    SMTPCommand,
    SMTPMatchContains,
    SMTPStatusCode,
)

MAIL_SERVER_HOST = "mock-smtp"
MAIL_SERVER_SMTP_PORT = 25
MAIL_SERVER_API_PORT = 8000
MAX_IS_READY_ATTEMPTS = 20
CHECK_IS_READY_SECONDS = 1
EXP_LOG_ERROR_MSG = "An error occurred in sending email for NO more candy"

logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def docker_compose():
    here = pathlib.Path(__file__).parent.resolve()
    with DockerCompose(here, compose_file_name=["docker-compose.yml"], pull=True) as compose:
        host = compose.get_service_host(MAIL_SERVER_HOST, MAIL_SERVER_SMTP_PORT)
        smtp_port = int(compose.get_service_port(MAIL_SERVER_HOST, MAIL_SERVER_SMTP_PORT))
        api_port = int(compose.get_service_port(MAIL_SERVER_HOST, MAIL_SERVER_API_PORT))
        yield MockSmtpConf(host, smtp_port, api_port)
        stdout, stderr = compose.get_logs()
        logger.info("Docker compose stdout: %s", stdout)
        logger.info("Docker compose stderr: %s", stderr)


@pytest.fixture(scope="function")
def mock_smtp(docker_compose: MockSmtpConf):
    mock = MockSmtp(conf=docker_compose)
    attempts = 0
    while not mock.is_ready():
        attempts += 1
        if attempts > MAX_IS_READY_ATTEMPTS:
            raise Exception("MOCK SMTP is not ready after max number of attempts reached")
        time.sleep(CHECK_IS_READY_SECONDS)

    try:
        yield mock
    finally:
        mock.clean_up()


@pytest.fixture(scope="function")
def candy_box(docker_compose: MockSmtpConf) -> CandyBox:
    conf_mail = ConfEmail(
        enable_send_email=True,
        host=docker_compose.host,
        port=docker_compose.smtp_port,
        from_addr="me@example.com",
        to_addrs=["you@example.com"],
    )

    dashboard = Dashboard(conf_mail)
    return CandyBox(dashboard=dashboard, number_candy=3)


def test_candy_box_no_mail(mock_smtp, candy_box):
    candy_box.eat_one()
    assert mock_smtp.get_mails() == []


def test_candy_box_two_mails(mock_smtp, candy_box):
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()
    assert len(mock_smtp.get_mails()) == 2
    # Compare first Mail
    compare_mail(mock_smtp.get_mails()[0])
    # Compare second mail
    compare_mail(mock_smtp.get_mails()[1])


# caplog is a pytest fixture used to capture log, see https://docs.pytest.org/en/6.2.x/fixture.html
def test_candy_box_failure(mock_smtp, candy_box, caplog):
    mock_smtp.set_behaviours(
        [
            SMTPBehaviour(
                command=SMTPCommand.MAIL_FROM,
                condition=SMTPMatchContains("me@example.com"),
                response=SMTPStatusCode.COMMAND_NOT_IMPLEMENTED_502,
            )
        ]
    )
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()

    assert len(mock_smtp.get_mails()) == 0
    assert [record for record in caplog.get_records(when="call") if record.getMessage() == EXP_LOG_ERROR_MSG]


def compare_mail(mail: Mail) -> None:
    assert mail.from_addr == "me@example.com"
    assert mail.to_addrs == ["you@example.com"]
    assert mail.subject == "No more candy!!!"
    assert mail.body == "Oh no! No more candy..."
