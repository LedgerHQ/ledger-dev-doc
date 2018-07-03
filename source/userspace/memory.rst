Persistent Storage and PIC
==========================

BOLOS applications have access to two different types of memory in the Secure
Element: a small amount of RAM for the call stack and certain global variables,
and a considerably larger amount of flash memory for persistent storage. Access
to flash memory is regulated by the Memory Protection Unit which is configured
by BOLOS to prevent applications from tampering with parts of flash memory that
they shouldn't. However, applications are able to access the part of flash
memory where their constant data and code is defined. This data includes code
and ``const`` variables, but applications may also allocate extra space in NVRAM
to be used at runtime for persistent storage.

Types of Memory
---------------

All global variables that are declared as ``const`` are stored in read-only
flash memory, right next to code. All normal global variables that are declared
as non-``const`` are stored in RAM. However, thanks to the link script
(``script.ld``) in the SDK, global variables that are declared as non-``const``
and are given the prefix ``N_`` are placed in a special write-permitted location
of NVRAM. This data can be read in the same way that regular global variables
are read. However, writing to NVRAM variables must be done using the
``nvm_write(...)`` function defined by the SDK, which performs a syscall. When
loading the app, NVRAM variables are initialized with data specified in the
app's hex file (this is usually just zero bytes).

.. warning::

   Initializers of global non-``const`` variables (including NVRAM variables)
   are ignored. As such, this data must be initialized by application code.

.. _flash-memory-endurance:

Flash Memory Endurance
----------------------

The flash memory for the `ST31G480
<http://www.st.com/en/secure-mcus/st31g480.html>`_, which is the Secure Element
used in the Ledger Blue, is rated for 500 000 erase / write cycles. This should
be more than enough to last the expected lifetime of the device, but only if
applications use it properly. Applications should avoid erasures as much as
possible. Here are some techniques for avoiding wearing out the device's flash
memory.

Firstly, if you intend to be changing data in flash memory many times while an
application is running, consider caching the data in RAM and then flushing to
flash memory when the application has finished its operation. This of course has
the downside of possible data loss if the user powers off the device (perhaps by
unplugging it, in the case of the Nano S) before the data has been written to
persistent storage. Secondly, developers should be aware that flash memory pages
are aligned to 64-byte boundaries. The rating of 500 000 erase / write cycles
mentioned earlier means that each page in flash memory is expected to survive
500 000 erasures. As such, one can develop an application that writes to as few
pages as possible. For example, if you intend to store 32 bytes of data in flash
memory, write amplification can be avoided by making sure that 32 bytes of data
is contained entirely within a single page (and modified using only a single
call to ``nvm_write(...)``). If the data crossed a 64-byte page boundary, then
writing to it once may require two pages to be erased instead of just one.

In the future, Ledger will provide various persistent storage utilities within
BOLOS and the SDKs to simplify the process of using flash memory efficiently.

PIC and Model Implications
--------------------------

PIC stands for Placement Independent Code. The BOLOS toolchain produces PIC to
allow for the code **Link address** to be different from the code **Execution
address**. For example, the ``main`` function is linked in the generated
application at address ``0xC0D00000``. However, the slot used when loaded into
the Secure Element could be ``0x10E40400``. Therefore, if the code makes a
reference to ``0xC0D00000``, even with an offset, it would be denied access as
the application is locked by the Memory Protection Unit (not to mention, this is
not the correct address of the ``main`` function at runtime).

The PIC assembly generator makes sure every dereference is relative to the
Program Counter, and never to an arbitrary address resolved during the link
stage. This behavior is supported by clang versions 4.0.0 and later.

Traditionally, PIC code implies the BSS segment (RAM variables) is at a constant
offset of the code. For example, if code is at ``0xC0D00000``, then global vars
may be at ``0xC2D00000``, so if loaded at ``0x10E00000`` then global vars would
be at ``0x12E00000``. However, BOLOS uses a fixed address for global vars. The
global variables start address and length are defined in the link script. Only
the code is meant to be placed at different addresses (in flash memory, rather
than RAM).

The model we chose has limitations, which are related to the way ``const`` data
and code is referenced in other ``const`` data. Here is a simple example:

.. code-block:: c

   const char array1[] = {1, 2, 3, 4};
   const char array2[] = {1, 2, 3, 4};
   const char *array_2d[] = {array1, array2};

   void main() {
       int sum, i, j;
       sum = 0;
       for (i = 0; i < 2; i++) {
           for (j = 0; j < 4; j++) {
               sum += array_2d[i][j]; // Core Fault!
           }
       }
   }

In the example above, when dereferencing ``array_2d``, the compiler uses a
link-time address (in the ``0xC0D00000`` space, following the previous
examples). This is not where the program is loaded in memory at runtime.
Therefore, when the dereference is executed, it causes a Core Fault that
effectively stalls the SE. Luckily, the solution is pretty simple, thanks to a
small piece of assembly provided with the SDKs which is invoked with the
``PIC(...)`` macro. ``PIC(...)`` uses the current load address to adjust the
link-time address in order to acquire the correct runtime address of ``const``
data and code. The above examples can be corrected by modifying the line where
``array_2d`` is dereferenced to do the following:

.. code-block:: c

    sum += ((const char*) PIC(array_2d[i]))[j];

The same mechanism must be applied when storing function pointers in ``const``
data. The PIC call cast is just different. Additionally, if a non-link-time
address is passed to ``PIC(...)``, then it will be preserved. This is possible
due to the wisely chosen link-time address which is beyond both real RAM and
loadable addresses. For example, ``PIC(...)`` is used during a call to
``io_seproxyhal_display_default(...)``, all display elements can hold a
reference to a string to be displayed with the element, and the string could be
in RAM or code, and therefore ``PIC(...)`` is applied to acquire the correct
runtime address of the string, even if it's in RAM.
