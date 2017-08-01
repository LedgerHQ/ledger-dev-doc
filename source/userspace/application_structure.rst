Application Structure and I/O
=============================

Many of the existing BOLOS applications are based on a smartcard architecture.
This is because BOLOS applications are not meant to run standalone, but rather
assist a host process (on a computer / smartphone) to perform a secure task
(signing a message, encryption / decryption, etc.). Therefore the device is
commonly addressed using a command / response scheme. Numerous design decisions
have been made when developing the SDKs in order to support this model.

However, the Event / Commands / Status model is designed to avoid limitations on
the application, as it does not follow the command / response synchronous model.
Developers are free to work around the model and redesign a custom event
processing loop to suit their needs.

APDU Interpretation Loop
------------------------

The command / response scheme used to address the device is similar to the
`ISO/IEC 7816-4
<https://en.wikipedia.org/wiki/Smart_card_application_protocol_data_unit>`_
smartcard protocol. Each command / response packet is called an APDU. The
application is driven by a never-ending APDU interpretation loop called straight
from the application main function.

Each cycle of the APDU interpretation loop calls ``io_exchange(...)`` from the
SDK, which first sends a response APDU (unless it's the first call, in which
case it sends nothing), and then receives the next command APDU.

However, sometimes, a user confirmation to perform a security action must be
performed before replying to an APDU (for example, when signing a message). Such
behavior is handled by replying no data to the command in the APDU interpreter
by using the ``IO_REPLY_ASYNCH`` flag, then following the user action calling
``io_exchange`` with the ``IO_RETURN_AFTER_TX`` flag and with the amount of data
to reply to the stalled command.

For an example of this feature, refer to `blue-app-samplesign
<https://github.com/LedgerHQ/blue-sample-apps/blob/2fb0f8f68ef68bbecd601cf476e532177288a0fa/blue-app-samplesign/src/main.c>`_.
In this app, when the command APDU to sign a message is received (line 510), the
flag ``IO_ASYNCH_REPLY`` is set and no response APDU is sent. If the user
approves the action, then the button push handler calls
``io_seproxyhal_touch_approve(...)`` which sends the response APDU using another
call to ``io_exchange(...)`` with the ``IO_RETURN_AFTER_TX`` flag set (line
434). The same occurs if the user denies the action, in which case
``io_seproxyhal_touch_deny(...)`` is triggered.

Protocols
---------

It's important to understand that the APDU protocol used by most BOLOS
applications is not implemented by BOLOS itself. Instead, the APDU
interpretation is performed entirely by the SDK. This means that applications
can choose to implement another protocol on top of the transport layer (USB HID,
USB CCID, BLE, ...) instead of APDU. In fact, the same is true for the transport
layer protocols. Applications can customize the way the application is
enumerated as a USB device by the host.

.. figure:: images/common_protocols.png
   :align: center

   Common protocols across BOLOS applications

Unprocessed Events
------------------

APDU processing relies on the BOLOS way of framing / transporting APDU packets.
All event processing related to transfer operations (including USB) is performed
within ``io_exchange(...)``. Not considering customization of the transport,
some Events are not automagically processed by ``io_exchange(...)`` (for
example: Button Push Events, Display Processed Events, Ticker Events, ...). In
order to handle these events that cannot be handled automagically,
``io_exchange(...)`` calls ``io_event(...)`` which is defined by the application
(not by the SDK).

Developers must take great care in the way they process Events. Events might
occur in the middle of APDU transport (most likely Button Push or Ticker
Events). As such, ``io_event(...)`` must return ``1`` if events are expected,
otherwise the current APDU transport will be terminated (this feature could be
used to implement a timeout, for example).

Thanks to a hardware buffer in the SE, it is impossible to miss an Event packet.
And, due to the E/Cs/S protocol design, no Event will be sent by the MCU until a
new Status is sent by the application.
