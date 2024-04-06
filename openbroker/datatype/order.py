from typing import Dict, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import uuid

from ..constant.order import OrderType, ProductType, PositionType


@dataclass
class OrderParams(ABC):

    def __str__(self):
        # print the class name and the dataclass attributes (order params)
        return f'<{self.__class__.__name__} {self.__dict__}>'

    @abstractmethod
    def dump(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def load(cls, order_info: dict) -> "OrderParams":
        pass


@dataclass
class MarketOrderParams(OrderParams):
    """ Dataclass representing the parameters of a market order """
    reference_price: float = 0.0

    def dump(self) -> dict:
        return {
            'ref_price': self.reference_price,
            'order_type': OrderType.Market.value
        }

    @classmethod
    def load(cls, order_info: dict) -> "MarketOrderParams":
        return cls(
            reference_price=order_info.get('ref_price', 0.)
        )


@dataclass
class LimitOrderParams(OrderParams):
    """ Dataclass representing the parameters of a limit order """
    limit_price: float

    def dump(self) -> dict:
        return {
            'price': self.limit_price,
            'order_type': OrderType.Limit.value
        }

    @classmethod
    def load(cls, order_info: dict) -> "LimitOrderParams":
        return cls(
            limit_price=order_info['price']
        )


@dataclass
class StopLossOrderParams(OrderParams):
    """ Dataclass representing the parameters of a stop loss order """
    limit_price: float
    trigger_price: float

    def dump(self) -> dict:
        return {
            'limit_price': self.limit_price,
            'trigger_price': self.trigger_price,
            'order_type': OrderType.StopLoss.value
        }

    @classmethod
    def load(cls, order_info: dict) -> "StopLossOrderParams":
        return cls(
            limit_price=order_info['limit_price'],
            trigger_price=order_info['trigger_price']
        )


ORDER_TYPE_PARAMS: Dict[OrderType, OrderParams] = {
    OrderType.Market: MarketOrderParams,
    OrderType.Limit: LimitOrderParams,
    OrderType.StopLoss: StopLossOrderParams
}
ORDER_PARAMS_TYPE = {ORDER_TYPE_PARAMS[order_type]: order_type for order_type in ORDER_TYPE_PARAMS}


@dataclass
class PlaceOrderRequestParams:
    """ Dataclass representing the place request parameters of a single order  """
    instrument_id: str
    symbol: str
    product_type: ProductType
    side: PositionType
    quantity: int
    order_info: OrderParams
    tags: Dict[str, str] = field(default_factory=lambda: {})
    user_tag: str = ''

    def dump(self) -> dict:
        value = {
            'instrument_id': self.instrument_id,
            'symbol': self.symbol,
            'product_type': self.product_type.value,
            'side': self.side.value,
            'quantity': self.quantity,
            'order_info': self.order_info.dump(),
            'extra_tags': self.tags
        }
        if self.user_tag:
            value['user_tag'] = self.user_tag
        return value

    @classmethod
    def load(cls, order_req: dict) -> "PlaceOrderRequestParams":
        return cls(
            instrument_id=order_req['instrument_id'],
            symbol=order_req['symbol'],
            product_type=order_req['product_type'],
            side=order_req['side'],
            quantity=order_req['quantity'],
            order_info=ORDER_TYPE_PARAMS[order_req['order_info']['order_type']].load(order_req['order_info']),
            tags=order_req.get('extra_tags', {}),
            user_tag=order_req.get('user_tag', '')
        )


@dataclass
class ModifyOrderRequestParams:
    """ Dataclass representing the modify request parameters of a single order  """
    order_id: uuid.UUID
    order_info: OrderParams

    def dump(self) -> dict:
        return {
            'order_id': self.order_id,
            'order_info': self.order_info.dump()
        }

    @classmethod
    def load(cls, order_req: dict) -> "ModifyOrderRequestParams":
        return cls(
            order_id=order_req['order_id'],
            order_info=ORDER_TYPE_PARAMS[order_req['order_info']['order_type']].load(order_req['order_info'])
        )
    

@dataclass
class PlaceResponse:
    """ Dataclass representing the response of a single place order  """
    success: bool
    order_id: Union[uuid.UUID, None]
    tags: Dict[str, str] = field(default_factory=lambda: {})
    user_tag: str = ''

    @classmethod
    def load(cls, data: dict) -> "PlaceResponse":
        return cls(
            success=data['success'],
            order_id=data.get('order_id'),
            user_tag=data.get('user_tag', ''),
            tags=data.get('extra_tags', {}),
        )


@dataclass
class ModifyResponse:
    """ Dataclass representing the response of a single modify order  """
    success: bool
    msg: str = ''

    @classmethod
    def load(cls, data: dict) -> "ModifyResponse":
        return cls(
            success=data['success'],
            msg=data.get('msg', '')
        )
    

@dataclass
class CancelResponse:
    """ Dataclass representing the response of a single cancel order  """
    success: bool
    msg: str = ''

    @classmethod
    def load(cls, data: dict) -> "CancelResponse":
        return cls(
            success=data['success'],
            msg=data.get('msg', '')
        )
