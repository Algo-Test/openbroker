from typing import Union, Dict, List
import inspect

from .api import UsersAPI
from .constant.broker import Broker
from .entity.broker import BrokerConnection, parse_broker_connection
from .broker_login import BROKER_LOGIN_ROUTINES
from .session import UserSession


class BrokersClient:

    def __init__(self, user_session: UserSession) -> None:
        self.__users_api = UsersAPI(user_session=user_session)
        self._user_session = user_session
        self.__broker_connections: Dict[Broker, BrokerConnection] = {}
    
    @property
    def brokers(self):
        """ Dictionary representing broker connections. """
        return self.__broker_connections

    def update_brokers(self):
        """ Fetch the list of brokers connected by the user and update the internal state """
        brokers: List[Dict] = self.__users_api.fetch_brokers()['brokers']

        updated_connections = {}
        for broker in brokers:
            if broker.get('app_keys') is None:
                continue
            
            broker_type = broker['broker']
            updated_connections[broker_type] = parse_broker_connection(broker)

        self.__broker_connections = updated_connections

    def refresh_broker(self, broker_type: Broker):
        broker = self.__broker_connections.get(broker_type)
        if broker is None:
            raise ValueError(f'Broker {broker_type} not found')

        broker_data = self.__users_api.get_broker(broker.id)
        self.__broker_connections[broker_type] = parse_broker_connection(broker_data)

    def login_broker(self, broker_type: Broker, **kwargs):
        """Login to the broker - Experimental feature currently implemented for a few brokers (Zerodha and XTS brokers)
        """

        broker = self.__broker_connections.get(broker_type)
        if broker is None:
            raise ValueError(f'Broker {broker_type} not found')

        login_routine = BROKER_LOGIN_ROUTINES.get(broker_type)

        if login_routine is None:
            raise NotImplementedError(f'Broker login not implemented for {broker_type}')

        # ensure the passed kwargs match the positional args for the login function
        login_func_args = inspect.signature(login_routine).parameters.keys()
        login_func_args = set(login_func_args) - {'api', 'broker', 'kwargs'}
        kwargs_keys = set(kwargs.keys())

        if login_func_args != kwargs_keys:
            raise Exception(f'Invalid arguments passed to login function.'
                            f'Expected: {login_func_args}, Got: {kwargs_keys}')

        login_routine(self.__users_api, broker, **kwargs)

        # if no exception raised, fetch the user's broker details again
        self.refresh_broker(broker_type)

    # TODO: better not renaming enums around the codebase
    # TODO: should instead raise a not found exception?
    def get_broker(
            self,
            broker_type: Broker = None,
            broker_id: str = None,
            api_key: str = None
    ) -> Union[BrokerConnection, None]:
        """
        Get a broker configured in the user's account.
        Use any of the kwargs to select the broker. Only one of the kwargs may be provided at a time.

        :param broker_type: Broker enum
        :param broker_id: broker id
        :param api_key: broker api key
        :return: BrokerConnection if requested broker is found, None otherwise
        """

        # only one of the kwargs may be provided at a time
        if sum([broker_type is not None, broker_id is not None, api_key is not None]) != 1:
            raise ValueError('Exactly one of broker_type, broker_id, or api_key must be provided')

        if broker_type is not None:
            return self.__broker_connections.get(broker_type)

        elif broker_id is not None:
            return next(
                filter(lambda b: b.id == broker_id, self.__broker_connections.values()),
                None
            )

        else:
            return next(
                filter(lambda b: b.api_key == api_key, self.__broker_connections.values()),
                None
            )


class BrokerLoginParams:
    pass


class ZerodhaLoginParams(BrokerLoginParams):
    api_key: str
    totp: int
