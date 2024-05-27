
from typing import List, Set
import uuid

from .base import BaseAPI
from ..config import Config
from ..datatype.order import PlaceOrderRequestParams, ModifyOrderRequestParams


class InstrumentsAPI(BaseAPI):
    
    def get_instruments(self):
        return self._request(
            "GET",
            f"{Config.feed_base_url}/contracts"
        )
