from enum import Enum


class Segment(str, Enum):
    """
    Enum representing the type of an instrument: Equity, Future, Option.
    """
    Cash = 'CASH'
    Future = 'FUT'
    Option = 'OPT'


class OptionType(str, Enum):
    """
    Enum representing the type of an option: Call or Put.
    """
    Call = 'CE'
    Put = 'PE'