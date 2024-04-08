=============
API Reference
=============


OpenBroker client
=================

    The main client and entry point to AlgoTest APIs.

    It provides authentication and session management for the APIs and exposes the following interfaces:
    - Brokers API :class:`~openbroker.broker.BrokersClient` for broker information lookup
    - Instruments API :class:`~openbroker.instrument.InstrumentsClient` for instrument information lookup
    - Orders API :class:`~openbroker.order.OrdersClient` for order management

.. autoclass:: openbroker.OpenBroker

    **Attributes**

    .. attribute:: brokers

        The :class:`~openbroker.broker.BrokersClient` instance for broker information lookup

    .. attribute:: instruments

        The :class:`~openbroker.instrument.InstrumentsClient` instance for instrument information lookup

    .. attribute:: orders

        The :class:`~openbroker.order.OrdersClient` instance for order management

    **Methods**

    .. automethod:: connect

    .. automethod:: close


Brokers interface
=================

.. autoclass:: openbroker.BrokersClient
    :members:
    :inherited-members:

.. autoclass:: openbroker.entity.BrokerConnection()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load


Instruments interface
=====================

.. autoclass:: openbroker.InstrumentsClient
    :members:
    :inherited-members:

.. autoclass:: openbroker.datatype.Instrument()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load, load_json


Orders interface
================

.. autoclass:: openbroker.OrdersClient
   :members:
   :inherited-members:


Order objects
-------------

:class:`~openbroker.entity.Order` is a dataclass representing an existing order in the system.

.. autoclass:: openbroker.entity.Order()
    :member-order: bysource
    :undoc-members:
    :exclude-members: load


Order parameters
................

Order parameters are specific to the order type and are used to create or modify an order.


.. autoclass:: openbroker.datatype.order.OrderParams()

.. autoclass:: openbroker.datatype.MarketOrderParams
    :show-inheritance:
    :member-order: bysource
    :undoc-members: false
    :exclude-members: load

.. autoclass:: openbroker.datatype.LimitOrderParams
    :show-inheritance:
    :member-order: bysource
    :undoc-members:
    :exclude-members: load

.. autoclass:: openbroker.datatype.StopLossOrderParams
    :show-inheritance:
    :member-order: bysource
    :undoc-members:
    :exclude-members: load


Enums and constants
...................

.. autoclass:: openbroker.constant.Broker()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load

.. autoclass:: openbroker.constant.ProductType()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load

.. autoclass:: openbroker.constant.PositionType()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load

.. autoclass:: openbroker.constant.OrderStatus()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load


Place/Modify/Cancel orders interfaces
-------------------------------------

Place order
...........

.. autoclass:: openbroker.datatype.PlaceOrderRequestParams()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load, dump

.. autoclass:: openbroker.datatype.PlaceResponse()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load


Modify order
............

.. autoclass:: openbroker.datatype.ModifyOrderRequestParams()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load, dump

.. autoclass:: openbroker.datatype.ModifyResponse()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load


Cancel order
............

.. autoclass:: openbroker.datatype.CancelResponse()
    :member-order: bysource
    :members:
    :undoc-members:
    :exclude-members: load
