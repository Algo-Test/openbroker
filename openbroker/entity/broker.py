from typing import Union, Dict
import logging
import datetime

from ..constant.broker import Broker

logger = logging.getLogger(__name__)


class BrokerConnection:
    id: str
    broker_type: Broker
    api_key: str

    def __init__(
            self,
            id: str, 
            broker_type: Broker, 
            api_key: str, 
            logged_until: Union[datetime.datetime, None]
    ):
        """
        Represents a broker account registered on AlgoTest.in
        :param id:
        :param broker_type:
        :param api_key:
        :param logged_until:
        """
        self.id = id
        self.broker_type = broker_type
        self.api_key = api_key
        self.__logged_until = logged_until

    def __str__(self):
        class_name = self.__class__.__name__
        return f'<{class_name}:{self.id} - {self.broker_type}[{self.api_key}] {self.logged_in}>'

    @property
    def logged_in(self) -> bool:
        """ Boolean flag exposing the broker status. True if the broker is logged in for the trading day. """
        if self.__logged_until is None:
            return False
        return self.__logged_until > datetime.datetime.utcnow()


def parse_broker_connection(broker_data: Dict) -> BrokerConnection:
    return BrokerConnection(
        id=broker_data['_id'],
        broker_type=broker_data['broker'],
        api_key=broker_data['app_keys']['ApiKey'],
        logged_until=datetime.datetime.fromisoformat(
            broker_data['logged_until']
        ) if broker_data['logged_until'] else None
    )