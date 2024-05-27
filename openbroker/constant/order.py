import enum


class OrderType(str, enum.Enum):
    """
    Enum representing the type of an order: Market, Limit, StopLoss.
    """
    Market = 'OrderType.Market'
    Limit = 'OrderType.Limit'
    StopLoss = 'OrderType.StopLoss'


class ProductType(str, enum.Enum):
    """
    Enum representing the product type of an order: MIS or NRML.
    """
    MIS = 'ProductType.MIS'
    NRML = 'ProductType.NRML'


class PositionType(str, enum.Enum):
    """
    Enum representing the side of an order: Buy or Sell.
    """
    Buy = 'PositionType.Buy'
    Sell = 'PositionType.Sell'


class OrderStatus(str, enum.Enum):
    """
    Enum representing the status of an order
    """
    Open = 'Open'
    TriggerPending = 'Trigger Pending'
    PlacePending = 'Place Pending'
    ModifyPending = 'Modify Pending'
    CancelPending = 'Cancel Pending'
    Canceled = 'Canceled'
    Rejected = 'Rejected'
    Completed = 'Completed'
