from typing import Dict, Union
from typing import TextIO
import logging
import requests
import json
import dataclasses
from copy import copy, deepcopy

from .api import InstrumentsAPI
from .datatype.instrument import Instrument, Segment, OptionType

logger = logging.getLogger(__name__)


class InstrumentsClient:
    def __init__(self):
        self.__api = InstrumentsAPI()
        self._contracts: Union[Dict, None] = None

    @property
    def instruments(self):
        # return a deep copy of the instrument map to prevent accidental modification
        return deepcopy(self._contracts)

    def dump(self, file: Union[str, TextIO]):
        """
        Dump the contract map to a file for later use
        :param file: a path or a file object
        """

        if not isinstance(file, (str, TextIO)):
            raise Exception("Invalid file argument. Please provide a file path or a file object")

        if self._contracts is None:
            raise Exception("Contract map not found. Please call update() or load() method.")

        # convert the Instrument objects to dicts to make it JSON serializable
        dump_dict = deepcopy(self._contracts)
        for underlying, underlying_data in dump_dict.items():

            underlying_data[Segment.Cash] = dataclasses.asdict(underlying_data[Segment.Cash])

            for expiry, instrument in underlying_data[Segment.Future].items():
                underlying_data[Segment.Future][expiry] = dataclasses.asdict(instrument)

            for expiry, instruments in underlying_data[Segment.Option].items():
                instruments = [dataclasses.asdict(i) for i in instruments]
                underlying_data[Segment.Option][expiry] = instruments

        if isinstance(file, str):
            with open(file, "w") as f:
                f.write(json.dumps(dump_dict))

        elif isinstance(file, TextIO):
            file.write(json.dumps(dump_dict))

    def load(self, file: Union[str, TextIO]):
        """
        Load the contract map from a file
        :param file: a path or a file object
        """
        if isinstance(file, str):
            with open(file, "r") as f:
                contracts = json.loads(f.read())

        elif isinstance(file, TextIO):
            contracts = json.loads(file.read())

        else:
            raise Exception("Invalid file argument. Please provide a file path or a file object")

        # convert the instrument dictionaries into Instrument objects
        for underlying, underlying_data in contracts.items():

            underlying_data[Segment.Cash] = Instrument.load_json(underlying_data[Segment.Cash])

            for expiry, instrument_dict in underlying_data[Segment.Future].items():
                underlying_data[Segment.Future][expiry] = Instrument.load_json(instrument_dict)

            for expiry, instrument_dicts in underlying_data[Segment.Option].items():
                instruments = [Instrument.load_json(i) for i in instrument_dicts]
                underlying_data[Segment.Option][expiry] = instruments

        self._contracts = contracts

    def update(self):
        """
        Fetch the updated contract map from AlgoTest API
        :return:
        """
        try:
            contracts = self.__api.get_instruments()
            self._contracts = self._parse_contracts(contracts)

        except requests.exceptions.JSONDecodeError:
            logger.exception("Failed to decode response from API")
            raise Exception("Failed to update contract map")

        except requests.exceptions.RequestException as exc:
            logger.exception("Failed to fetch contract map from API")
            raise Exception("Failed to update contract map")

        except Exception:
            logger.exception("Failed to parse contract map")
            raise Exception("Failed to update contract map")

    @staticmethod
    def _parse_contracts(contracts: dict):

        if 'underlying_map' not in contracts:
            raise ValueError("Invalid contract map format")

        contracts = contracts['underlying_map']
        parsed_contracts_dict = {}

        for underlying, underlying_data in contracts.items():
            parsed_contracts_dict[underlying] = {}

            for instrument_type, data in underlying_data.items():

                if instrument_type == Segment.Cash:
                    assert isinstance(data, dict)
                    contract = data
                    parsed_contracts_dict[underlying][Segment.Cash] = Instrument.load(contract)

                elif instrument_type == Segment.Future:
                    parsed_contracts_dict[underlying][Segment.Future] = {}
                    for expiry, contract in data.items():
                        parsed_contracts_dict[underlying][Segment.Future][expiry] = Instrument.load(contract)

                elif instrument_type == Segment.Option:
                    parsed_contracts_dict[underlying][Segment.Option] = {}
                    for expiry, contracts in data.items():
                        parsed_options = [Instrument.load(contract) for contract in contracts]
                        parsed_contracts_dict[underlying][Segment.Option][expiry] = parsed_options

                else:
                    logger.warning(f"Ignoring invalid instrument type in contract map: {instrument_type}")

        return parsed_contracts_dict

    # TODO: should we raise an exception or return None when a contract is not found?
    def find_instrument(
            self,
            underlying: str,
            segment: Segment,
            expiry: str = None,
            strike: float = None,
            option_type: Union[str, OptionType] = None
    ) -> Union[Instrument, None]:
        """
        Find an instrument matching the kwargs options from all available instruments.

        :param underlying: The underlying symbol (i.e. 'NIFTY')
        :param segment: The segment of the instrument (i.e. Segment.Future)
        :param expiry: Expiry of the instrument, if applicable, for futures and options (i.e. '2023-12-28')
        :param strike: Strike price of the option, if applicable (i.e. 15000)
        :param option_type: Option type, if applicable (i.e. OptionType.Call)
        :return: Instrument object if found, None otherwise
        """

        if self._contracts is None:
            raise Exception("Contract map not found. Please call update method.")

        # validate arguments
        if segment == Segment.Cash:
            if expiry or strike or option_type:
                raise ValueError("Invalid arguments for Cash instrument")
        elif segment == Segment.Future:
            if strike or option_type:
                raise ValueError("Invalid arguments for Future instrument")
        elif segment == Segment.Option:
            if not all([expiry, strike, option_type]):
                raise ValueError("Missing arguments for Option instrument")
        else:
            raise ValueError(f"Unsupported instrument type: {segment}")

        # if underlying not found raise exception
        if underlying not in self._contracts:
            raise Exception(f"Underlying {underlying} not available in contract map")

        # search for the instrument
        instrument = None

        if segment == Segment.Cash:
            instrument = self._contracts[underlying][Segment.Cash]

        elif segment == Segment.Future:
            instrument = self._contracts[underlying][Segment.Future].get(expiry, None)

        elif segment == Segment.Option:
            expiry_options = self._contracts[underlying][Segment.Option].get(expiry, [])
            instrument = next(
                filter(
                    lambda instr: instr.option_type == option_type and instr.strike == strike,
                    expiry_options
                ),
                None
            )

        return copy(instrument)
