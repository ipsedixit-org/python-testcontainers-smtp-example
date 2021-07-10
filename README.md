# Python testcontainers smtp example

A full example of sending an email using testcontainers and a mock smtp server.

In a nutsheel there is a candy box with a limited number of candies.
When all candies are eat then an alarm is sent to the dashboard and then an email.

For smtp server is used a (James Mock server)[https://medium.com/linagora-engineering/a-mock-smtp-server-for-remote-mail-delivery-testing-2d1a2cfd2798],as described in (my previous post)[https://ipsedixit.org/blog/2021/2021-06-03-mock-smtp-server.html].


__**Note:**__ This project has used as a base (pypa sample project)[https://github.com/pypa/sampleproject].

## Initial setup
Create virtualenv using make command
```bash
make setup
```

## Execute test
```bash
make test
```

### Execute a single test
```bash
source .venv/bin/activate
pytest --log-cli-level DEBUG --capture=tee-sys tests_integration/test_candy_with_mock_smtp_server.py
```

## Code linting
Code linting has been done using (black)[https://github.com/psf/black] and (isort)[https://pycqa.github.io/isort/].
```bash
make lint
```