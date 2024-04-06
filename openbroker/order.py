from typing import Dict, List, Union
import time
import uuid
import logging

from .api import OrdersAPI, WsAPI
from .config import Config
from .datatype.order import PlaceOrderRequestParams, ModifyOrderRequestParams
from .datatype.order import PlaceResponse, ModifyResponse, CancelResponse
from .entity.broker import BrokerConnection
from .entity.order import Order
from .session import UserSession

logger = logging.getLogger(__name__)


class OrdersClient:

    def __init__(self, user_session: UserSession, orders_group_tag: str = '') -> None:
        if len(orders_group_tag) > 32:
            raise ValueError('Order API supports max 32 characters in user tag')

        self.__user_session = user_session
        self._user_tag = orders_group_tag

        self.__orders_api = OrdersAPI(user_session=self.__user_session)

        self.__orders_dict: Dict[uuid.UUID, Order] = {}
        self.__ws_connection: Union[WsAPI, None] = None

    @property
    def all_orders(self):
        """ Dictionary representing all orders. """
        # TODO: should probably return a RO view (deepcopy) of the dict
        return self.__orders_dict

    def __fetch_tagged_orders(self) -> None:
        if not self._user_tag:
            return

        response = self.__orders_api.get_order_by_user_tag(user_tag=self._user_tag)
        for order_dict in response:
            self.__update_order(Order.load(order_dict))

    def __update_order(self, new_update: Order) -> None:
        order_id = new_update.order_id

        update_dict = True
        if order_id in self.__orders_dict:
            old_update = self.__orders_dict[order_id]
            update_dict = new_update.updated_at >= old_update.updated_at

        if update_dict:
            self.__orders_dict[order_id] = new_update

    def __update_order_callback(self, order_update: dict) -> None:
        # noinspection PyBroadException
        try:
            if self._user_tag and order_update.get('user_tag') != self._user_tag:
                return
            
            new_update = Order.load(order_update)
            self.__update_order(new_update)

        except Exception:
            logger.exception(f"Error in processing ws callback payload: {order_update}")

    def connect(self, ws_update=True, fetch_prev_orders=True):
        """
        Establish a connection to the Orders API Update Websocket, and fetches previous orders, if required.

        :param ws_update: If websocket should be enabled for orders update
        :param fetch_prev_orders: If previous orders placed with the same orders_group_tag are to be fetched
        :return: None
        """

        if fetch_prev_orders:
            self.__fetch_tagged_orders()

        if ws_update:
            self.__ws_connection = WsAPI(
                user_session=self.__user_session,
                ws_url=Config.ws_url,
                callback_func=self.__update_order_callback
            )
            self.__ws_connection.start()
            time.sleep(1)
    
    def close(self):
        if self.__ws_connection is not None:
            self.__ws_connection.stop()
    
    def get_order(self, order_id: uuid.UUID, force_fetch=False) -> Order:
        """
        Fetch the order object associated with the order_id.
        If the order is not available and updated in memory, it is fetched via API request.
        Specifying force_fetch=True will always fetch the order via API request.

        :param order_id: UUID of the order
        :param force_fetch: always fetch the order via API request
        :return: The requested order, if found
        """
        assert order_id

        # fetch the order if explicitly requested or if:
        #   - the order is not in the cache
        #   - the order updates websocket is not active
        force_fetch = (
                force_fetch
                or order_id not in self.__orders_dict
                or self.__ws_connection is None
                or not self.__ws_connection.is_connected
        )

        if not force_fetch:
            return self.__orders_dict[order_id]

        response = self.__orders_api.get_order(order_id=order_id)
        order = Order.load(response)
        # TODO: what if the order is not found?

        self.__update_order(order)
        return order
    
    def place_orders(
            self,
            broker_connection: BrokerConnection,
            order_list: List[PlaceOrderRequestParams]
    ) -> List[PlaceResponse]:
        """
        Place orders in a single API call.

        The API supports placing up to 10 orders in a single call.

        :param broker_connection: the broker the orders are to be placed with
        :param order_list: list of place orders requests
        :return: list of PlaceResponse objects for each order placed (sorting is maintained)
        """
        
        assert 0 < len(order_list) <= 10
        assert broker_connection.logged_in

        for order in order_list:
            if len(order.tags) > 3:
                raise ValueError('Order API supports max 3 tags')
            
            for key, value in order.tags.items():
                if len(key) > 20:
                    raise ValueError('Order API supports max 20 characters in tag key')
                if len(value) > 30:
                    raise ValueError('Order API supports max 30 characters in tag value')
            
            if self._user_tag:
                order.user_tag = self._user_tag

        response = self.__orders_api.place_orders(broker_id=broker_connection.id, order_list=order_list)
        return [PlaceResponse.load(data) for data in response]
    
    def modify_orders(self, order_list: List[ModifyOrderRequestParams]) -> Dict[uuid.UUID, ModifyResponse]:
        """
        Modify orders in a single API call.

        The API supports modifying up to 10 orders in a single call.

        :param order_list: list of modify requests
        :return: dictionary of order_id: ModifyResponse pairs for each order
        """
        assert 0 < len(order_list) <= 10

        response = self.__orders_api.modify_orders(order_list=order_list)
        return {
            order_id: ModifyResponse.load(modify_response) for order_id, modify_response in response.items()
        }

    def cancel_orders(self, order_list: List[uuid.UUID]) -> Dict[uuid.UUID, CancelResponse]:
        """
        Cancel orders in a single API call.

        :param order_list: list of order ids to be cancelled
        :return: dictionary of order_id: CancelResponse pairs for each order
        """

        assert 0 < len(order_list) <= 10

        response = self.__orders_api.cancel_orders(order_ids=set(order_list))
        return {
            order_id: CancelResponse.load(cancel_response) for order_id, cancel_response in response.items()
        }
