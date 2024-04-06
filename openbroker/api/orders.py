
from typing import List, Set
import uuid

from .base import BaseAPI
from ..config import Config
from ..datatype.order import PlaceOrderRequestParams, ModifyOrderRequestParams


class OrdersAPI(BaseAPI):
    
    def place_orders(self, broker_id: str, order_list: List[PlaceOrderRequestParams]):
        return self._request(
            "POST",
            f"{Config.order_base_url}/place",
            data={
                'broker_id': broker_id,
                'orders': [order.dump() for order in order_list]
            }
        )
    
    def modify_orders(self, order_list: List[ModifyOrderRequestParams]):
        return self._request(
            "PUT",
            f"{Config.order_base_url}/modify",
            data={
                'orders': [order.dump() for order in order_list]
            }
        )
    
    def cancel_orders(self, order_ids: Set[uuid.UUID]):
        return self._request(
            "POST",
            f"{Config.order_base_url}/cancel",
            data=list(order_ids)
        )
    
    def get_todays_orders(self):
        return self._request(
            "GET",
            f"{Config.order_base_url}/today-orders"
        )
    
    def get_order(self, order_id: uuid.UUID):
        return self._request(
            "GET",
            f"{Config.order_base_url}/order?order_id={order_id}"
        )
    
    def get_order_by_user_tag(self, user_tag: str):
        return self._request(
            "GET",
            f"{Config.order_base_url}/orders-by-user-tag?user_tag={user_tag}"
        )
