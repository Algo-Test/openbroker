import time
import logging
import configparser

from openbroker import OpenBroker
from openbroker.constant import Broker, ProductType, PositionType, OrderStatus, Segment, OptionType
from openbroker.datatype import PlaceOrderRequestParams, ModifyOrderRequestParams
from openbroker.datatype import MarketOrderParams, LimitOrderParams, StopLossOrderParams


# read credentials from credentials.ini file
config = configparser.ConfigParser()
config.read('credentials.ini')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


UNDERLYING = "FINNIFTY"
EXPIRY = "2024-04-02"
STRIKE = 21200
QTY = 40
SL_PER = 50
PRODUCT_TYPE = ProductType.MIS


ob = OpenBroker(config.get("user", "PHONE_NUMBER"), config.get("user", "PASSWORD"), "920straddle")
ob.connect(instrument_filepath="contracts.json")

broker_connection = ob.brokers.get_broker(Broker.IIFL)

call_instrument = ob.instruments.find_instrument(UNDERLYING, Segment.Option, EXPIRY, STRIKE, OptionType.Call)
put_instrument = ob.instruments.find_instrument(UNDERLYING, Segment.Option, EXPIRY, STRIKE, OptionType.Put)
logger.info(f"Call: {call_instrument} . Put: {put_instrument}")


call_entry_tag = "call_entry"
put_entry_tag = "put_entry"
call_exit_tag = "call_exit"
put_exit_tag = "put_exit"
tag_key = "leg"


call_entry_request = PlaceOrderRequestParams(
    instrument_id=call_instrument.token,
    symbol=call_instrument.symbol,
    product_type=PRODUCT_TYPE,
    side=PositionType.Sell,
    quantity=QTY,
    order_info=MarketOrderParams(),
    tags={tag_key: call_entry_tag}
)

put_entry_request = PlaceOrderRequestParams(
    instrument_id=put_instrument.token,
    symbol=put_instrument.symbol,
    product_type=PRODUCT_TYPE,
    side=PositionType.Sell,
    quantity=QTY,
    order_info=MarketOrderParams(),
    tags={tag_key: put_entry_tag}
)


## Take Entry: Sell a call and a PUT
response = ob.orders.place_orders(broker_connection, [call_entry_request, put_entry_request])

entry_order_ids = {call_entry_tag: None, put_entry_tag: None}
for resp in response:
    if tag_key not in resp.tags:
        continue
    tag = resp.tags[tag_key]
    entry_order_ids[tag] = resp.order_id
logger.info(entry_order_ids)


#Wait for entries to complete
while True:
    open_orders = []
    time.sleep(1)

    for _, order_id in entry_order_ids.items():
        order = ob.orders.get_order(order_id)
        
        if order.status == OrderStatus.Completed or order.status == OrderStatus.Rejected or order.status == OrderStatus.Canceled:
            continue
        
        open_orders.append(order_id)

    if open_orders:
        continue
    
    break


call_entry_price = ob.orders.get_order(entry_order_ids[call_entry_tag]).average_price
put_entry_price = ob.orders.get_order(entry_order_ids[put_entry_tag]).average_price

call_sl = int(call_entry_price*(1+SL_PER/100)*20)/20
put_sl = int(put_entry_price*(1+SL_PER/100)*20)/20

logger.info(f"Entry Taken. Call entry@{call_entry_price}. SL@{call_sl}")
logger.info(f"Entry Taken. Put entry@{put_entry_price}. SL@{put_sl}")

assert call_entry_price > 0
assert put_entry_price > 0


call_exit_request = PlaceOrderRequestParams(
    instrument_id=call_instrument.token,
    symbol=call_instrument.symbol,
    product_type=PRODUCT_TYPE,
    side=PositionType.Buy,
    quantity=QTY,
    order_info=StopLossOrderParams(limit_price=call_sl+2, trigger_price=call_sl),
    tags={tag_key: call_exit_tag}
)

put_exit_request = PlaceOrderRequestParams(
    instrument_id=put_instrument.token,
    symbol=put_instrument.symbol,
    product_type=PRODUCT_TYPE,
    side=PositionType.Buy,
    quantity=QTY,
    order_info=StopLossOrderParams(limit_price=put_sl+2, trigger_price=put_sl),
    tags={tag_key: put_exit_tag}
)


## Place SL Orders
response = ob.orders.place_orders(broker_connection, [call_exit_request, put_exit_request])

exit_order_ids = {call_exit_tag: None, put_exit_tag: None}
for resp in response:
    if tag_key not in resp.tags:
        continue
    tag = resp.tags[tag_key]
    exit_order_ids[tag] = resp.order_id
logger.info(exit_order_ids)


#Wait for exit to complete
modified_orders = False
cutoff_time = time.time() + 60

while True:
    curr_time = time.time()

    if curr_time > cutoff_time and not modified_orders:
        modify_requests = [ModifyOrderRequestParams(order_id=order_id, order_info=MarketOrderParams()) for order_id in exit_order_ids.values()]
        modify_response = ob.orders.modify_orders(modify_requests)

        modified_orders = all([resp.success for resp in modify_response.values()])
        logger.info(modify_response)
    
    open_orders = []
    time.sleep(1)
    for _, order_id in exit_order_ids.items():
        order = ob.orders.get_order(order_id)
        
        if order.status == OrderStatus.Completed or order.status == OrderStatus.Rejected or order.status == OrderStatus.Canceled:
            continue
        
        open_orders.append(order_id)

    if open_orders:
        continue
    
    break


call_exit_price = ob.orders.get_order(exit_order_ids["call_exit"]).average_price
put_exit_price = ob.orders.get_order(exit_order_ids["put_exit"]).average_price

logger.info(f"Call exited @ {call_exit_price}")
logger.info(f"Put exited @ {put_exit_price}")

ob.close()