from dataclasses import dataclass

import uuid
import logging
import datetime

from ..constant.order import PositionType, ProductType, OrderStatus
from ..datatype.order import OrderParams, ORDER_TYPE_PARAMS

logger = logging.getLogger(__name__)


@dataclass
class Order:
    """
    Class representing all the properties of and order that has been placed.

    Attributes:
        instrument_id (str): The instrument id of the order.
        symbol (str): The symbol of the order.
        side (Side): The side, buy or sell, of the order.
        product_type (ProductType): The product type of the order (MIS or NRML).
        order_params (OrderParams): The type and parameters of the order (Market, Limit, ...).
        quantity (int): The quantity of the order.
        broker (Broker): The broker where the order is executed.
        order_id (int): The internal order id of the order.
        broker_order_id (str): The broker order id of the order.
        status (OrderStatus): The status of the order.
    """

    order_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime

    user_tag: str
    extra_tags: dict

    instrument_id: str
    symbol: str
    product_type: ProductType
    side: PositionType
    quantity: int
    lot_size: int
    order_info: OrderParams
    broker_id: str
    user_id: str

    broker_order_id: str
    status: OrderStatus

    rejection_code: str
    rejection_reason: str
    trade_time: str
    filled_quantity: int
    average_price: float

    @classmethod
    def load(cls, order_data: dict) -> "Order":
        return cls(
            order_id=order_data['order_id'],
            created_at=order_data['created_at'],
            updated_at=order_data['updated_at'],

            user_tag=order_data['user_tag'],
            extra_tags=order_data['extra_tags'],
            
            instrument_id=order_data['instrument_id'],
            symbol=order_data['symbol'],
            product_type=order_data['product_type'],
            side=order_data['side'],
            quantity=order_data['quantity'],
            lot_size=order_data['lot_size'],
            order_info=ORDER_TYPE_PARAMS[order_data['order_info']['order_type']].load(order_data['order_info']),
            broker_id=order_data['broker_id'],
            user_id=order_data['user_id'],

            broker_order_id=order_data['broker_order_id'],
            status=order_data['status'],

            rejection_code=order_data['rejection_code'],
            rejection_reason=order_data['rejection_reason'],
            trade_time=order_data['trade_time'],
            filled_quantity=order_data['filled_quantity'],
            average_price=order_data['average_price']
        )
