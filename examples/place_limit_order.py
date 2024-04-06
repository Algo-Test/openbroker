import logging
import time
import configparser

from openbroker import OpenBroker
from openbroker.constant import Broker, ProductType, PositionType, Segment, OptionType
from openbroker.datatype import PlaceOrderRequestParams, LimitOrderParams


# read credentials from credentials.ini file
config = configparser.ConfigParser()
config.read('credentials.ini')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ob = OpenBroker(config.get("user", "PHONE_NUMBER"), config.get("user", "PASSWORD"))
ob.connect(instrument_filepath="contracts.json")

broker_connection = ob.brokers.get_broker(Broker.IIFL)

contract = ob.instruments.find_instrument('NIFTY', Segment.Option, '2024-04-25', 22900, OptionType.Call)
logger.info(contract)

order_req = PlaceOrderRequestParams(
    instrument_id=contract.token,
    symbol=contract.symbol,
    product_type=ProductType.MIS,
    side=PositionType.Buy,
    quantity=50,
    order_info=LimitOrderParams(limit_price=0.05)
)

logger.info(order_req)
response = ob.orders.place_orders(broker_connection, [order_req])
logger.info(response)

order_id = response[0].order_id
time.sleep(2)

order_status = ob.orders.get_order(order_id)
logger.info(order_status)

ob.close()