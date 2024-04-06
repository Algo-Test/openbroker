from typing import Union, Dict
import requests

from ..session import UserSession
from ..exceptions import InvalidDataException, RequestFailedException


class BaseAPI:
    def __init__(self, user_session: UserSession = None):
        # if no user session is provided, create a new unauthenticated session
        self._session = user_session or UserSession('', '', requests.Session(), {})

    def _request(self, 
            method: str, 
            url: str, 
            data: Union[Dict, None] = None, 
            params: Union[Dict, None] = None
        ) -> Dict:
        
        method = method.upper()

        r = self._session.request_session.request(
            method=method,
            url=url,
            json=data,
            params=params,
            timeout=(self._session.connect_timeout, self._session.read_timeout),
            headers=self._session.request_headers
        )

        if r.status_code == 200:
            try:
                return r.json()
            except ValueError:
                raise InvalidDataException(str(r.content))
        else:
            raise RequestFailedException(str(r.content))
