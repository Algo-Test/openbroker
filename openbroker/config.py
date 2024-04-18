import os
from .utils import str_to_bool


class Config:
    __is_uat_env = str_to_bool(os.environ.get('OPENBROKER_UAT', 'False'))

    base_url = 'https://algotest.in/api'
    
    broker_login_url = 'https://algotest.in/api/broker_login'

    feed_base_url = 'https://algotest.in/api/pricefeed'
    
    order_base_url = 'https://algotest.in/api/orders-uat' if __is_uat_env else 'https://algotest.in/api/orders'

    ws_url = 'wss://algotest.in/api/orders-uat/updates' if __is_uat_env else 'wss://algotest.in/api/orders/updates'
