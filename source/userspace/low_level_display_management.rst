============================
Low-level display management
============================

.. warning:: 

   This article only concerns about 1% of users who wish to get a deeper understanding / design more advanced flows. Feel free to skip it!

The BOLOS SDKs contain a toolkit for building GUIs called the BOLOS Application
Graphics Library (BAGL). BAGL defines a few useful types, most notably
``bagl_element_t``. This type defines a single display element, such as a
rectangle, a line of text, a touchable button (in the case of the Ledger Blue),
et cetera. Therefore, an entire GUI consists of an entire array of such
elements. As the device hardware, including the screen, is managed by the MCU,
the BAGL elements need to be transported to the MCU over SEPROXYHAL in order to
display them. This is done using a Display Status.

A Display Status may be used to send a single BAGL element to the MCU. However,
due to the design of the E/Cs/S protocol, in order to send a sequence of BAGL
elements the application must asynchronously send Display Statuses and wait for
Display Processed Events before sending the next one, as well as handling the
other Events that are received from the MCU in the mean time. As this is
something that must be done by every BOLOS application, a set of utilities have
been defined in the SDK to facilitate this process. These utilities also
simplify the process of handling user input events, such as button presses.

Asynchronous Display and Interaction Helpers
--------------------------------------------

To facilitate the process of implementing an asynchronous display manager loop,
a set of macros have been defined in the BOLOS SDKs. All these macros have the
prefix ``UX_``, and use a global variable of type ``ux_state_t`` called ``ux``
to maintain the user interface state.


``UX_INIT(...)``
   This macro is to be called when initializing the application, prior to
   sending the first Display Status.

``UX_DISPLAY(...)``
   This macro takes an array of BAGL elements to be displayed and renders them,
   asynchronously. It is to be called when a new screen is to be displayed over
   the current one. This macro only sends the first element of the given array
   using a Display Status. Therefore, further Commands and Statuses are
   prohibited until the Display Processed Event is sent by the MCU.

``UX_REDISPLAY()``
   This macro restarts the process of drawing the current screen. It behaves
   like ``UX_DISPLAY(...)``, but takes no arguments.

``UX_DISPLAYED()``
   This macro returns 0 when the array requested to be displayed by
   ``UX_DISPLAY(...)`` or ``UX_REDISPLAY()`` has not been displayed entirely, or
   a non-zero value when it has.

``UX_DISPLAYED_EVENT(...)``
   This macro is to be called to handle Display Processed Events (generally in
   the ``io_event(...)`` function). It displays the next element in the array
   given as a parameter to ``UX_DISPLAY(...)``. This macro sends a Display
   Status if an element remains to be displayed in the given array. Therefore,
   further Commands and Statuses are prohibited until the Display Processed
   Event is sent by the MCU.

``UX_BUTTON_PUSH_EVENT(...)``
   This macro facilitates handling of Button Push Events, by setting the button
   released flag and calling the button handler implicitly passed to
   ``UX_DISPLAY(...)``.

See `the sample apps <https://github.com/LedgerHQ/blue-sample-apps>`_ for
examples of how to use these macros. The main concept to remember is that after
a Display Status has been sent, the application must wait, asynchronously, for
the Display Processed Event before being able to continue to display more
elements of the GUI.

.. _bolos-ux:

BOLOS UX
--------

The BOLOS UX is the implementation of the device-wide user interface; it is a
component of the :ref:`dashboard <dashboard>`. Applications delegate certain
jobs to the BOLOS UX in order to retain consistency across all apps for certain
UI components (like the status bar on the Ledger Blue), as well as to allow the
operating system to override the application's UI when necessary (for example,
when locking the screen). The application interfaces with the BOLOS UX using
``os_ux(...)``, which is a syscall. However, applications don't need to call
this function directly as it is automatically called by the display interaction
helpers (the ``UX_`` macros).

Applications should delegate Events like Button Push Events to the BOLOS UX (in
this case, using ``UX_BUTTON_PUSH_EVENT(...)``) instead of handling them
directly in case the BOLOS UX needs to override the application's UI. If the
event is consumed by the BOLOS UX (for example, a button press while the user is
unlocking the screen) then the event is not passed on to the application.
