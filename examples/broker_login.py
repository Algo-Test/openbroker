import logging
import configparser

from openbroker import BrokersClient
from openbroker.session import generate_session
from openbroker.constant import Broker


# read credentials from credentials.ini file
config = configparser.ConfigParser()
config.read('credentials.ini')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# AlgoTest credentials
phone_number = config.get("user", "PHONE_NUMBER")
password = config.get("user", "PASSWORD")

# Zerodha credentials
zerodha_client_id = config.get("zerodha", "ZERODHA_ID")
zerodha_password = config.get("zerodha", "ZERODHA_PASS")
zerodha_totp_secret = config.get("zerodha", "ZERODHA_TOTP_SECRET")


user_session = generate_session(phone_number, password)
broker_client = BrokersClient(user_session=user_session)
broker_client.update_brokers()

broker_connection = broker_client.get_broker(Broker.Zerodha)
logger.info(broker_connection)

try:
    broker_client.login_broker(
        Broker.Zerodha,
        client_id=zerodha_client_id,
        password=zerodha_password,
        totp_secret=zerodha_totp_secret
    )

except:
    logger.exception("Error in broker login")
