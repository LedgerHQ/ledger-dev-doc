Common Pitfalls and Troubleshooting
===================================

In this section, we'll walk you through a lot of concepts that are hard to grasp
when developing on the BOLOS platform, and we'll provide some analysis of common
failure scenarios that you might experience while developing applications.

Not Enough RAM
--------------

At the time of this writing, the default link script provided by the SDK for the
Ledger Nano S allocates 4 KiB of RAM for applications to use. This 4 KiB has to
be enough to store all global non-const and :doc:`non-NVRAM <memory>` variables
as well as the call stack (which is currently set to 768 bytes by default, also
defined in the link script).

This is the linker error you will experience if you declare too many global
non-const and non-NVRAM variables to fit in RAM:

.. code-block:: none

   bin/app.elf section `.bss' will not fit in region `SRAM'

The only solution to this problem is, of course, using less RAM. You can
accomplish this by making your application's memory layout more efficient.
Alternatively, if you're feeling adventurous, you can attempt to modify the link
script (``script.ld`` in the SDKs) to optimize the space allocated for the call
stack. If you choose to pursue the latter option, we recommend you read the next
section as well.

Stack Overflows
---------------

Determining the exact amount of the call stack used by your application can be
difficult to do without simply running your application. The technique we
recommend for avoiding stack overflows is using a stack canary. Creating a stack
canary involves setting a magic value at the start of the stack area (the stack
grows towards lower addresses, so a canary at the start of this region will be
located at the top of the stack), and then the canary is checked regularly. If
the canary was modified, then this means there was a stack overflow.

In a future version of the BOLOS SDKs, this feature will be implemented
automatically. Until then, this is the recommended way to implement a stack
canary:

.. code-block:: c

   // This symbol is defined by the link script to be at the start of the stack
   // area.
   extern unsigned long _stack;

   #define STACK_CANARY (*((volatile uint32_t*) &_stack))

   void init_canary() {
       STACK_CANARY = 0xDEADBEEF;
   }

   void check_canary() {
       if (STACK_CANARY != 0xDEADBEEF)
           THROW(EXCEPTION_OVERFLOW);
   }

The canary should be checked regularly. For example, you could run the check
every time ``io_event(...)`` is called.

Error Handling
--------------

Error handling in C can sometimes be a bit counter-intuitive. With our error
model, there are two common failure scenarios.

Firstly, you must take care to always close a try context when jumping out of
it. For example, in the block of code below, the ``CLOSE_TRY`` macro must be
used to close the try context before returning from the function in the case
that ``i > 0``. However, in the ``CATCH`` clause, the try has already been
closed automatically so ``CLOSE_TRY`` is not necessary.

.. code-block:: c

   bool is_positive(int8_t i) {
       BEGIN_TRY {
           TRY {
               if (i == 0)
                   THROW(EXCEPTION);
               if (i > 0) {
                   CLOSE_TRY;
                   return true;
               }
           } CATCH_OTHER(e) {
               return false;
           } FINALLY {}
       } END_TRY;
       return false;
   }

Another common failure scenario is caused by the compiler making invalid
assumptions when optimizing your code because it doesn't understand how our
exception model works. To avoid this problem, when modifying variables within a
try / catch / finally context, always declare those variables ``volatile``.

.. code-block:: c

   uint16_t multiply(uint8_t a, uint8_t b) {
       volatile uint16_t product = 0;
       volatile uint8_t multiplier = b;
       while (true) {
           BEGIN_TRY {
               TRY {
                   if (multiplier == 0)
                       THROW(1);
                   multiplier--;
                   product += a;
                   THROW(2);
               } CATCH_OTHER(e) {
                   if (e == 1)
                       return product;
               } FINALLY {}
           } END_TRY;
       }
       // Suppress compiler warning
       return 0;
   }

In the above example, ``a`` does not need to be declared ``volatile`` because it
is never modified.

On another note, you should use the error codes defined in the SDKs wherever
possible (see ``EXCEPTION``, ``INVALID_PARAMETER``, etc. in ``os.h``). If you
decide to use custom error codes, never use an error code of ``0``.

Application Stalled
-------------------

An application stalling when run on the device (the device's screen freezes and
stops responding to APDU) could be caused by a number of issues from the SE
being isolated due to invalid handling of SEPROXYHAL packets, to a core fault on
the device (perhaps due to a misaligned memory access or an attempt to access
restricted memory). If this occurrs, it is best to attempt to simplify the app
and strip away as much code as possible until the problem can be isolated.

Unaligned RAM access
--------------------

.. code-block:: c

  uint16_t *ptr16 = &tmp_ctx.signing_context.buffer[processed]; 
  PRINTF("uint16_t: %d", ptr16[0]);

``ptr16[0]`` access can be stalling the app, even though ``tmp_ctx.signing_context.buffer[processed]`` (``unsigned char*``) can be accessed alright. This happens when pointer isn't word-aligned, but word is access in RAM. Workaround is copying buffer into another location which is properly aligned (e.g. using `os_memmove`).

Please refer to the :ref:`alignment <alignment>` page for further information.
