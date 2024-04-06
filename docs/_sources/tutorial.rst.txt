========
Tutorial
========

This tutorial will guide you through understanding the OpenBroker framework and how to ...
To follow through this tutorial you need an AlgoTest account with a connected broker and the openbroker package installed.
If you don't have an account, you can create one by visiting the AlgoTest website.
The package can be installed using pip:

.. code-block:: python

    pip install openbroker
..

TIP: Testing out and developing in an advanced environment like Jupyter Notebook is recommended.
Advanced IDEs such as PyCharm or Visual Studio Code also provide type hinting and static analysis.


Connecting with AlgoTest account
================================

We start by instantiating an OpenBroker object with the AlgoTest account credentials.
The OpenBroker object is the main interface to the AlgoTest API and represents a user session with AlgoTest.

.. code-block:: python

    openbroker = OpenBroker(username='your_username', password='your_password')

Note: be careful in sharing your credentials with others. It is recommended to store your credentials in a secure way.
This tutorial stores them in plain text for simplicity. Look at the examples in the examples folder for a more secure way to store your credentials.

After instantiating the OpenBroker client, we can login with the AlgoTest API by calling the connect method.

.. code-block:: python

    openbroker.connect()
..

The connect method will authenticate the user with the AlgoTest API and establish a session.
The connect method also loads the user's account information and useful market data.


Fetching brokers
================

Once connected, we can get the list of available brokers and their connection status from `BrokersClient`.

The `brokers` property returns a dictionary of Broker objects.

`get_broker()` instead returns a single Broker object based on the provided filter.

.. code-block:: python

    brokers_client = openbroker.brokers
    zerodha_broker = brokers_client.get_broker(broker_type=Broker.Zerodha)
    dhan_broker = brokers_client.get_broker(api_key='my-dhan-api-key')

    print(zerodha_broker.api_key)
    print(zerodha_broker.logged_in)
..


Placing an order
================

It's possible to place an order with any logged-in broker by calling the place_order method.
All it takes is defining a PlaceOrderRequest object and passing it to the place_order method.

.. code-block:: python
    
    contract = openbroker.instruments.find_instrument('NIFTY', Segment.Option, '2024-04-25', 22900, OptionType.Call)
    order_req = PlaceOrderRequestParams(
        instrument_id=contract.token,
        symbol=contract.symbol,
        product_type=ProductType.MIS,
        side=PositionType.Buy,
        quantity=50,
        order_info=LimitOrderParams(limit_price=0.05)
    )
    
    broker_connection = openbroker.brokers.get_broker(Broker.IIFL)
    response = openbroker.orders.place_orders(broker_connection, [order_req])
    order_id = response[0].order_id
..