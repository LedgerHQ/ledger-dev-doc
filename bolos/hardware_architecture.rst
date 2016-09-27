.. _bolos-hardware-architecture:

Hardware architecture
=====================

Before explaining how applications perform, let’s take a look at the hardware architecture to better embrace the hardware related constraints before analyzing their software implications.

Environment
-----------

In BOLOS architecture, everything is done to empower application with full control of the device features. This has the tremendous advantage of not limiting what an application can really do - each application executes in a “virtual” device and can reconfigure all the hardware. It also implies developers might have to deal with many technical details themselves if no common source layers are available (which is only the case for custom I/O protocols).

.. _app-centric-view:

.. figure:: /images/bolos_fig01.png
   :alt: application centric view
   
   Application centric view

:numref:`Figure %s <app-centric-view>` shows a view of the system as seen by the application. It directly accesses multiple peripherals and is the real brain of the device while it is running. Each box can be seen as a coprocessor, under direct command of the application.

Some peripheral are meant not only to receive commands, but also to trigger events. This is the case for buttons, activated upon user actions, and I/O peripherals which can perform background communication (f.e. USB: control transfers) or convey requests to be processed by the application.

In this model, the application is at the center, and is not relying on other embedded co-application.

Delegation model
----------------

BOLOS defines a two layer delegation model. Firstly, once it runs the application, BOLOS is not reachable anymore, it only provide basic services to the application during its execution. Secondly, and as a consequence, BOLOS is not processing commands and therefore does not alter Input/Output operations. 

Featuring these two key points, applications are in charge on the device. And it allows them to customize not only the display, but user input actions, and by extension, the way the device is enumerated on USB. If an application requires a Mass Storage emulation, or being seen as a WinUSB peripheral, it’s only a matter of event processing.

.. image:: /images/bolos_fig02.png
Figure 2: USB delegation overview

Closer look, multiple processors, Secure Element proxy
------------------------------------------------------

After the previous overview let’s dive into the actual hardware architecture supporting BOLOS.

.. image:: /images/bolos_fig03.png
Figure 3: detailed BOLOS architecture

BOLOS is split on 2 hardware chips, one being secure, the other having JTAG enabled and acting as a proxy. 

The Secure Element is split in 2 parts, one part under NDA and with hardware/software interaction, the other part being application loaded, open source friendly.

BOLOS relies on the collaboration of both chips to empower Secure Element applications. At first glance, and even at second and all following, the Secure Element is a very powerful piece of hardware but lacks inputs/outputs. In our architecture, we solved this problem by appending a chip full of inputs/outputs acting as a proxy for the Secure Element to explore new horizons. Not considering security implications (to be detailed in a security oriented document later on), and thanks to a simple asynchronous protocol, the Secure Element drives the proxy, which can be seen as a supercharged coprocessor of the Secure Element.

The SE-MCU link protocol is called SEPROXYHAL or SEPH in source code/documentation.

Event, Commands and Status
--------------------------

The SE-MCU link is a serialized list of 3 types of packets: events, commands and statuses. With the current implementation, if the packets are messed up, the SE ends up isolated and unable to communicate. When developing an application this is the most common failure scenario. Hopefully, multiple levels of software guards are provided to avoid such cases. 

The protocol works as follows: 
1. MCU sends an event (button press, ticker, USB transfer ...)
2. SE optionally issues a list of commands in response to the event
3. SE issues a status indicating the event is fully processed and waits for another event

.. image:: /images/bolos_fig04.png
Figure 4: SEPROXYHAL protocol concept

As a matter of fact, and due to buffer size, display requests are sent using status. Therefore, displaying multiple elements on the screen requires an asynchronous process sending display statuses, and waiting for displayed events. 

The SE throws an exception to applications willing to send more than one status in a row, without a new event being fetched in between.

Isolated single task model
--------------------------

Due to its limited ram size, the Secure Element is designed to only support one application running at a time. However, and for internationalization/customization purpose, the BOLOS Loader task is split in two parts : the logic/security scheme and the presentation/user interaction layer. The latter is called BOLOS UX.

BOLOS UX offers quite a few display primitives that are usable by the user.

This isolated model implies once the application is running, no other application can spuriously disturb the SE-MCU link. It also means that the application is in full control of all communication peripherals.