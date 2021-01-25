Emulating devices with Speculos
===============================

Ledger has developed its own Ledger Nano S / Ledger Nano X / Ledger Blue emulator, called `Speculos <https://github.com/LedgerHQ/speculos>`_. This emulator can be useful if you want to run tests, debug your app with GDB, or just try your app without having to physically plug-in your Ledger device.

We will go over quick guide to using speculos, but more information is available in the `docs section of the github page <https://github.com/LedgerHQ/speculos/tree/master/doc>`_.

Setup
-----

Make sure you have the appropriate packages installed on your machine::

    sudo apt install qemu-user-static python3-pyqt5 python3-construct python3-jsonschema python3-mnemonic python3-pyelftools gcc-arm-linux-gnueabihf libc6-dev-armhf-cross gdb-multiarch

Then build ::

    cmake -Bbuild -H.
    make -C build/

Pleaes note that the first build can take some time because a tarball of OpenSSL is downloaded (the integrity of the downloaded tarball is checked) before being built. Further invocations of ``make`` skip this step.

The following command line can be used for a debug build::

    cmake -Bbuild -DCMAKE_BUILD_TYPE=Debug -H.

Usage
-----

.. warning::

    Only run Speculos on trusted apps, as a malicious app could exploit it and make arbitrary Linux system calls.

To run your application, simply type in::

    ./speculos.py /path/to/app

You can then use your left / right arrows to emulate the left and right buttons of your device.

Debugging with GDB
------------------

Speculos can also be used to debug your code with GDB::

    ./speculos.py -d /path/to/app &
    ./tools/debug.sh /path/to/app
