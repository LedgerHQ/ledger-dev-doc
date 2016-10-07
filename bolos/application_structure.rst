Application structure
=====================

After the thorough look at the functional architecture, let's now dive into the application structure to play with the concepts described previously.

Many of the existing applications over BOLOS are based on a smartcard architecture. Indeed, BOLOS applications are not meant to run standalone, but rather assist a host process (on the computer/smartphone) to perform a secure task (signing a message, encryption/decryption). Therefore the device is commonly addressed using a command/response scheme. And from this assertion, numerous assertions are made in the coding patterns of the application.

However, the event/commands/status model is designed to avoid limitations on the application, as it does not follow the command/response synchronous model. Developers are free to work around the model and redesign a custom event processing loop to suit their needs.

Basically, an APDU (command) interpretation loop is called straight from the application main function, and dispatching the receiving commands to a subprocessor function.

APDU interpretation loop
------------------------

The command/response scheme in use in all our application is similar to the ISO 7816 smartcard protocol; It features an APDU interpretation loop, which is basically a never ending loop. The next command is fetched using common code of the SDK ``io_exchange``. The first call sends no data and receives the first command, the next call sends the response of the first command and receives the second command, and so on.

However, sometimes, a user confirmation to perform a security action is requested before replying to an APDU (for example when signing a message). Such behavior is handled by replying no data to the command in the APDU interpreter by using the ``IO_REPLY_ASYNCH`` flag, then following the user action calling ``io_exchange`` with the ``IO_RETURN_AFTER_TX`` flag and with the amount of data to reply to the stalled command.

Here is a sample micro application core that asks the user for a confirmation before replying to any command:

.. code-block:: c

    TBD

Unprocessed events
------------------

APDU processing relies on the BOLOS way of framing/transporting APDU packets. And all event processing related to transfer operations (including USB) are performed within ``io_exchange``. Not considering customization of the transport, some events are not automagically processed by ``io_exchange``, for example button press, displayed notification, ticker, among others. Io_exchange therefore calls ``io_event`` for all unprocessable event.

Developers must take great care in the way they process events. Indeed, events might occur in the middle of APDU transport, mostly button press or ticker notifications. Io_exchange will therefore trigger ``io_event``, which MUST reply 1 if events are expected, otherwise the current APDU transport will be terminated (which could be a feature for a timeout for example).

The developer doesn't have to be afraid of missing an event packet. Thanks to a hardware buffer in the SE, an event following a status cannot be missed. And as the MCU follows the E/Cs/S protocol, no event is to be received until a new status is sent by the application.

Asynchronous display and interaction helpers
--------------------------------------------

To make dealing with an asynchronous loop to request the display of User Interface elements on the screen easier, a set of macro and a global variable are available.


    ``UX_INIT``
        This macro is to be called when starting the application and prior to sending the first display status.

    ``UX_DISPLAY``
        This macro takes an array of elements to be displayed and renders them. It is to be called when a new screen is to be displayed over the current one. This macro only send the first element of the given array using a ``DISPLAY_STATUS``. Therefore further command and status are prohibited until the ``DISPLAY_PROCESSED_EVENT`` is sent by the MCU.

    ``UX_REDISPLAY``
        This macro restart drawing the current screen. It behaves like ``UX_DISPLAY`` but takes no arguments.

    ``UX_DISPLAYED``
        This macro return 0 when the array requested to be displayed by ``UX_DISPLAY`` or ``UX_REDISPLAY`` has not been displayed entirely.

    ``UX_DISPLAY_EVENT``
        This macro is to be called to process ``DISPLAY_PROCESSED`` events (generally in ``io_event`` function). It continue displaying elements of the array given as parameter to ``UX_DISPLAY``. This macro send a new ``DISPLAY_STATUS`` if an element remains to be displayed in the given array. Therefore further command and status are denied until the ``DISPLAY_PROCESSED`` event is received.

    ``UX_BUTTON_EVENT``
        This macro simplifies handling of button presses, especially inserting the ``RELEASED`` flag and calling the button handler implicitly given to ``UX_DISPLAY``.

See samples for call examples. However the main concept to remember is that after an display status has been issued, we must wait (asynchronously) for the display processed event before being able to interact with MCU.

PIC and model implications
--------------------------

PIC stands for Placement Independent Code. The BOLOS toolchain produces PIC to allow for the code Link address to be different from the code Execution address. For example, the main function is linked in the generated application at address ``0xC0D00000``. However the slot used when loaded into the Secure Element could be ``0x10E40400``. Therefore, if the code makes a reference to ``0xC0D00000``, even with an offset, it would be denied access as the application is locked by the Memory Protection Unit.

PIC assembly generator makes sure every dereference is relative to the Program Counter, and never to an arbitrary address resolved during the link stage. This behavior is enabled by the LLVM patch we provide.

Traditionally, PIC code implies the BSS (RAM variables) segment is at a constant offset of the code. (if code is @ ``0xC0D00000``, then vars are at ``0xC2D00000`` for example, so if loaded @ ``0x10E00000`` then vars would be @ ``0x12E00000``). But BOLOS have a fixed address for variables. Variables start address and length are defined in the link script. Only the code is meant to be placed at different addresses.

The model we chose has limitations, which are related to the way const data / code is dereferenced in other const data. Here is a simple example:

.. code-block:: c

    const char array1[]= {1,2,3,4};
    const char array2[]= {1,2,3,4};
    const char * arrayarray[]= {array1, array2};
    void main (void) {
      int sum, i, j;
      sum = 0;
      for (i=0;i<2; i++) {
        for (j=0; j<4; j++) {
          sum += arrayarray[i][j];
        }
      }
    }

In the previous source code, when dereferencing arrayarray, we obtain a linked address (in the ``0xC0D00000`` space, following previous samples). Which is not where the program is loaded in memory. Therefore, when the dereferencing is executed, it generates a Core Fault and somewhat exits the application or stall the SE. Either case, the solution is pretty simple, thanks to a small piece of assembly provided with SDK.

PIC is a macro and a function which adjust the link time address with the current load address.

Solution:

.. code-block:: c

    sum += ((const char*)PIC(arrayarray[i]))[j];

The same mechanism must be applied when storing function pointer. The PIC call cast is just different.

The key concept here is that PIC is safe to whatever is passed to it. This is thanks to the wisely chosen link time address which is beyond both real ram and loadable addresses. As an example, PIC is used during call to io_seproxyhal_display_default, all display elements can hold a reference onto a string to attach to display element, the string could be in RAM or code, and therefore PIC is to be applied to avoid a fault.

This problem shall be dealt with by a decent compiler with a static compile time analysis, but function pointers make it a real mess.

System calls requirements
-------------------------

BOLOS is based on an exception model for error reporting, therefore, it expects the application to call the BOLOS API using this mechanism. If an API function is called without such an open TRY CATCH context, then the BOLOS call is denied.

Here is a valid way to call a system entry point:

.. code-block:: c

    BEGIN_TRY {
      TRY {
        cx_hash_sha512(...);
      }
      FINALLY {
      }
    } END_TRY;

Error model
-----------

If you are used to C programming, error code is the default error model, setjmp and longjmp API might seem like a huge heap of problems lying ahead. However, when programming in embedded world, the traditional error model reaches its limit and, from past experience and projects, cost ~30% code when writing robust code. BOLOS is ported on quite a large piece of hardware but still, this is far too much. Therefore we've introduced a TRY/CATCH system supporting nesting (direct or transitive).

However there is a single constraint to be observed with our TRY/CATCH system, you must absolutely close TRY clause in an appropriate way. This means that return, break, continue or goto statement that jumps out of the TRY clause SHALL be avoided. It could lead to a crash of the application in a later THROW. As it is a denied behavior, you can use CLOSE_TRY to close each surrounding opened TRY clause that you're going to skip with the return, break, continue or goto statement. Only opened TRY { continue/return/break/goto } requires to be closed ; returning from CATCH or FINALLY is allowed (but still make sure you're not in a CATCH nested in a TRY).