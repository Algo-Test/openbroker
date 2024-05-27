import requests
import pyotp
from urllib.parse import urlparse

from .constant.broker import Broker
from .entity.broker import BrokerConnection
from .api import UsersAPI
from .config import Config


def xts_login(api: UsersAPI, broker: BrokerConnection):
    url = f"{Config.broker_login_url}/xts_confirm/{broker.id}"
    api._request("GET", url, params={'xts_broker': broker.broker_type})


def zerodha_login(
        api: UsersAPI, broker: BrokerConnection,
        client_id: str, password: str, totp_secret: str
):
    with requests.Session() as session:
        login_payload = {
            'user_id': client_id,
            'password': password,
        }
        login_response = session.post("https://kite.zerodha.com/api/login", data=login_payload, timeout=30)
        if login_response.status_code != 200:
            raise Exception(f"Error while logging in to kite for user-{client_id}, Error: {login_response.text}")

        req_id = login_response.json()['data']['request_id']
        twofa_payload = {
            'request_id': req_id,
            'user_id': client_id,
            'twofa_value': pyotp.TOTP(totp_secret).now(),
            'twofa_type': 'totp'
        }
        twofa_response = session.post("https://kite.zerodha.com/api/twofa", data=twofa_payload, timeout=30)
        if twofa_response.status_code != 200:
            raise Exception(f"Error while logging in to kite for user-{client_id}, Error: {twofa_response.text}")

        api_login_response = session.get(f"https://kite.zerodha.com/connect/login?v=3&api_key={broker.api_key}", timeout=30,
                                         allow_redirects=False)
        if api_login_response.status_code != 302:
            raise Exception(f"Error while logging in to kite for user-{client_id}, Error: {api_login_response.text}")

        finish_api_login_response = session.get(api_login_response.headers['Location'], timeout=30,
                                                allow_redirects=False)
        if finish_api_login_response.status_code != 302:
            raise Exception(
                f"Error while logging in to kite for user-{client_id}, Error: {finish_api_login_response.text}")

        location_url = finish_api_login_response.headers['Location']
        query_string = urlparse(location_url).query
        query_dict = dict(param.split('=') for param in query_string.split('&'))

        if 'request_token' not in query_dict:
            raise Exception(
                f"Error while logging in to kite for user-{client_id}. "
                f"Error: Request token unavailable in location url: {location_url}")

        request_token = query_dict['request_token']

    url = f"{Config.broker_login_url}/zerodha_confirm/{broker.id}"
    api._request("GET", url, params={'request_token': request_token})


BROKER_LOGIN_ROUTINES = {
    Broker.Zerodha: zerodha_login,
    # XTS brokers
    Broker.AcAgrawal: xts_login,
    Broker.BigulXTS: xts_login,
    Broker.FivePaisa: xts_login,
    Broker.IIFL: xts_login,
    Broker.JainamPro: xts_login,
    Broker.JainamXTS: xts_login,
    Broker.JMFL: xts_login,
    Broker.WisdomCapital: xts_login
}
