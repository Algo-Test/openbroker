from typing import Dict
import logging
from dataclasses import dataclass
import requests

from .config import Config

logger = logging.getLogger(__name__)


@dataclass
class UserSession:
    """ Session class to store user credentials and session token """
    user_id: str
    auth_token: str
    request_session: requests.Session
    request_headers: Dict
    connect_timeout: int = 5
    read_timeout: int = 10


def generate_session(phone_number: str, password: str, ssl_verify: bool = True) -> UserSession:
    """
    Login to AlgoTest.in with the user account and start a session

    :param phone_number: user phone number
    :param password: user password
    :return: UserSession
    """
    req_session = requests.Session()
    req_session.verify = ssl_verify

    response = req_session.post(
        f"{Config.base_url}/login",
        json={
            'phoneNumber': phone_number,
            'password': password
        },
    )
    response.raise_for_status()

    # fetch the access token in UserSession
    access_token_cookie = req_session.cookies.get('access_token_cookie')
    if access_token_cookie is None:
        raise Exception('Error fetching access JWT cookie while logging in')
    
    headers = {'X-CSRF-TOKEN-ACCESS': req_session.cookies.get('csrf_access_token')}

    return UserSession(
        user_id=response.json()['_id'],
        auth_token=access_token_cookie,
        request_session=req_session,
        request_headers=headers
    )
