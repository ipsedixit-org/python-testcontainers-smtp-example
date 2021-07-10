import pytest

from python_testcontainers_smtp_example.candy import ALARM_CANDY, CandyBox, ConfEmail, Dashboard


@pytest.fixture(scope="function")
def dashboard():
    conf_mail = ConfEmail(
        enable_send_email=False,
        host="fake-mail-server",
        port=25,
        from_addr="me@example.com",
        to_addrs=["you@example.com"],
    )

    yield Dashboard(conf_mail)


@pytest.fixture(scope="function")
def candy_box(dashboard):
    yield CandyBox(dashboard=dashboard, number_candy=3)


def test_candy_box_no_eat(candy_box):
    assert candy_box.has_more_candy()


def test_candy_box_eat_one(candy_box, dashboard):
    candy_box.eat_one()
    assert candy_box.has_more_candy()
    assert candy_box.remaining_candy() == 2
    assert dashboard.get_all_alarms() == []


def test_candy_box_eat_all_candy(candy_box, dashboard):
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()
    assert candy_box.has_more_candy() is False
    assert candy_box.remaining_candy() == 0
    assert dashboard.get_all_alarms() == []


def test_candy_box_eat_activate_alarm_one_time(candy_box, dashboard):
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()
    assert candy_box.has_more_candy() is False
    assert candy_box.remaining_candy() == 0
    assert dashboard.get_all_alarms() == [ALARM_CANDY]


def test_candy_box_eat_activate_alarm_two_times(candy_box, dashboard):
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()
    candy_box.eat_one()
    assert candy_box.has_more_candy() is False
    assert candy_box.remaining_candy() == 0
    assert dashboard.get_all_alarms() == [ALARM_CANDY, ALARM_CANDY]
