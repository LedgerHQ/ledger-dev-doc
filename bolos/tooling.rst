Tooling
=======

.. note:: Section in progress.

A system on its own could be the best but is useless if no tool to benefit from it.

    App source -> LLVM .o -> gnu ld -> hex -> python +icon -> device

Compiler toolchain
------------------

To support the code only PIC mode, a LLVM patchset is required. A docker image is available to make easier use of the compiler. Win32/64 builds are scheduled and will be made available soon.