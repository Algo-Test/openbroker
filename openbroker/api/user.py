from .base import BaseAPI
from ..config import Config


class UsersAPI(BaseAPI):
    
    def fetch_brokers(self):
        """ List all brokers """

        return self._request(
            "GET",
            f"{Config.base_url}/brokers"
        )
    
    def get_broker(self, broker_id: str):
        """ Get a single broker """

        return self._request(
            "GET",
            f"{Config.base_url}/broker/{broker_id}"
        )
