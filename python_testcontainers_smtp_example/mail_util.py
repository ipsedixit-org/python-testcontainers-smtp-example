import logging
import smtplib

logger = logging.getLogger(__name__)


def send(
    host: str,
    port: int,
    from_addr: str,
    to_addrs: list[str],
    subject: str,
    msg_body: str,
):
    """
    This a very pretty example of sending an email and there are some semplification.
    For example in sending an email could be more parameters (such as CopyCarbon), HTML and plain text, ...
    """
    logging.info("Try open connection to host: %s - port: %s", host, port)
    server = smtplib.SMTP(host=host, port=port)
    try:
        msg = f"Subject:{subject}\n\n{msg_body}"
        logging.info(
            "Send mail from_addr: %s - to_addrs: %s - msg: %s",
            from_addr,
            to_addrs,
            msg,
        )
        server.sendmail(from_addr=from_addr, to_addrs=to_addrs, msg=msg)
    finally:
        server.quit()
