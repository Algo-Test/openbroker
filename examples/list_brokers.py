import logging
import configparser

from openbroker import BrokersClient
from openbroker.session import generate_session


# read credentials from credentials.ini file
config = configparser.ConfigParser()
config.read('credentials.ini')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_session = generate_session(config.get("user", "PHONE_NUMBER"), config.get("user", "PASSWORD"))
broker_client = BrokersClient(user_session=user_session)
broker_client.update_brokers()

# available brokers can be listed through brokers property of ob.brokers
for broker_type, broker_connection in broker_client.brokers.items():
    logger.info(f"{broker_type}: {broker_connection}")
