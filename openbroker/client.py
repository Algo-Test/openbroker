from typing import Optional
import os

from .broker import BrokersClient
from .order import OrdersClient
from .instrument import InstrumentsClient
from .session import generate_session


class OpenBroker:
    """OpenBroker client. The main entry point to AlgoTest APIs.

    :param phone_number: User phone number
    :param password: User password
    :param user_tag: User tag assigned to orders
    """

    orders: Optional[OrdersClient]
    "API interface for orders"

    brokers: Optional[BrokersClient]
    "API interface for brokers"

    instruments: InstrumentsClient
    "API interface for instruments"

    def __init__(self, phone_number: str, password: str, orders_group_tag: str = ''):
        """
        Initialize the OpenBroker client with the user credentials
        :param phone_number: AlgoTest account phone number
        :param password: AlgoTest account password
        :param orders_group_tag: A common tag that a user wants to assign to all the orders placed by this client.
                         It's commonly used to identify a session or a strategy, by marking all the orders with the same identifier.
                         The identifier can be kept same across multiple sessions to track and restore the orders state.
        """
        self.phone_number = phone_number
        self.password = password
        self.orders_group_tag = orders_group_tag

        self.orders = None
        self.brokers = None
        self.instruments = InstrumentsClient()

    def connect(self, instrument_filepath: str = None):
        """
        Connect to AlgoTest account and initialize internal components to start using the APIs.
        It initializes the `OrdersClient`, establishing a websocket connection to receive order updates. And if a group tag was supplied
        during initialization, fetches state of all previous orders belonging to that tag.
        It also initializes the `BrokersClient`, fetching the list of brokers connected by the user.
        It also initializes the `InstrumentsClient`, fetching or restoring the list of instruments available for trading.
        It is recommended to provide a static instrument_filepath to avoid fetching instruments every time.
        
        :param instrument_filepath: Optional path to the file where instruments are stored. 
        :return:
        """
        user_session = generate_session(self.phone_number, self.password)

        self.orders = OrdersClient(user_session=user_session, orders_group_tag=self.orders_group_tag)
        self.brokers = BrokersClient(user_session=user_session)

        self.brokers.update_brokers()
        self.orders.connect()
        
        if instrument_filepath is not None and os.path.exists(instrument_filepath):
            self.instruments.load(instrument_filepath)
        else:
            self.instruments.update()
            if instrument_filepath is not None:
                self.instruments.dump(instrument_filepath)
        
    def close(self):
        """
        Close the OpenBroker API connection
        """
        if self.orders is not None:
            self.orders.close()

        self.orders = None
        self.brokers = None
