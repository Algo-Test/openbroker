from typing import Callable, Union

import threading
import websocket
import logging
import ssl
import time
# TODO: add orjson support in future versions for faster json parsing
import json

from ..session import UserSession

logger = logging.getLogger(__name__)


class WebsocketConnection:

    def __init__(self, user_session: UserSession, ws_url: str, callback_func: Callable):
        self._session = user_session
        self._url = ws_url
        self._callback = callback_func
        
        self.__websocket: Union[None, websocket.WebSocket] = None
        self.__ws_ssl = {"cert_reqs": ssl.CERT_NONE}

        self.__ws_thread = None
        self.__stop_event = threading.Event()

    @property
    def is_connected(self) -> bool:
        return self.__websocket is not None and self.__websocket.connected

    def start(self):
        """ Start the ws thread """
        
        self.__stop_event.clear()
        self.__ws_thread = threading.Thread(target=self.__run_ws, daemon=True)

        self.__ws_thread.start()
        logger.info(f'Listening for ws updates on {self._url}')

    def stop(self):
        """ Stop the ws thread """

        self.__stop_event.set()

        if self.is_connected:
            self.__websocket.close()
        
        if self.__ws_thread is not None:
            # wait for the thread to finish
            self.__ws_thread.join()
        
        logger.info(f'Stopped listening for ws updates from {self._url}')

    def __run_ws(self):
        """ Thread target function """

        while not self.__stop_event.is_set():
            message = None

            try:
                if self.__websocket is None:
                    self.__websocket: websocket.WebSocket = websocket.create_connection(
                        self._url,
                        sslopt=self.__ws_ssl,
                        cookie=f"access_token_cookie={self._session.auth_token}"
                    )

                message = self.__websocket.recv()
                if not message:
                    continue
                
                self._callback(json.loads(message))

            except (websocket.WebSocketConnectionClosedException, ssl.SSLZeroReturnError):
                logger.warning(f'Websocket connection closed for {self._url}')
                self.__websocket = None

            except Exception:
                logger.exception(f"Error in ws listen thread for {self._url}. msg={message}")
                time.sleep(1)
