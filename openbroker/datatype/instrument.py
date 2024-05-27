from typing import Union
from dataclasses import dataclass

from ..constant.instrument import Segment, OptionType

@dataclass
class Instrument:
    """Instrument dataclass representing an instrument and its properties.
    """

    token: str
    symbol: str
    underlying: str
    segment: Segment
    expiry: Union[str, None]
    strike: Union[float, None]
    option_type: Union[OptionType, None]
    lot_size: int
    tick_size: float
    max_qty_in_order: int
    exchange: str
    is_tradable: bool

    @classmethod
    def load(cls, instrument_data: dict) -> "Instrument":

        segment = Segment(instrument_data['instrument_type'])
        expiry, strike, option_type = None, None, None

        if segment == Segment.Future:
            expiry = instrument_data['expiry']
            strike = None
        elif segment == Segment.Option:
            expiry = instrument_data['expiry']
            strike = instrument_data['strike']
            option_type = OptionType(instrument_data['option_type'])

        return cls(
            token=instrument_data['token'],
            symbol=instrument_data['symbol'],
            underlying=instrument_data['underlying'],
            segment=segment,
            expiry=expiry,
            strike=strike,
            option_type=option_type,
            lot_size=instrument_data['lot_size'],
            tick_size=instrument_data['tick_size'],
            max_qty_in_order=instrument_data['max_qty_in_order'],
            exchange=instrument_data['exchange'],
            is_tradable=instrument_data['is_tradable']
        )

    @classmethod
    def load_json(cls, json_data: dict) -> "Instrument":
        # convert strings to enums where necessary
        segment = Segment(json_data['segment'])
        option_type = OptionType(json_data['option_type']) if json_data['option_type'] else None

        json_data['segment'] = segment
        json_data['option_type'] = option_type
        return cls(**json_data)

    def __str__(self):
        if self.segment == Segment.Cash:
            return f"{self.symbol} ({self.token}) [{self.segment.value}]"

        elif self.segment == Segment.Future:
            return f"{self.symbol} ({self.token}) [{self.segment.value}] {self.underlying} {self.expiry}"

        elif self.segment == Segment.Option:
            return (f"{self.symbol} ({self.token}) [{self.segment.value}] "
                    f"{self.underlying} {self.expiry} {self.strike} {self.option_type}")

        else:
            return f"Unknown instrument type: {self.segment}"
