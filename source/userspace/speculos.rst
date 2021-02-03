Emulating devices with Speculos
===============================

Ledger has developed its own Ledger Nano S / Ledger Nano X / Ledger Blue emulator, called `Speculos <https://github.com/LedgerHQ/speculos>`_. This emulator can be useful if you want to run tests, debug your app with GDB, or just try your app without having to physically plug-in your Ledger device.

We will go over quick guide to using speculos, but more information is available in the `docs section of the github page <https://github.com/LedgerHQ/speculos/tree/master/doc>`_.

Setup
-----

1. Start by cloning the `official Speculos repo <https://github.com/LedgerHQ/speculos>`_::

    git clone https://github.com/LedgerHQ/speculos

2. Make sure you have the appropriate packages installed on your machine::

    sudo apt install qemu-user-static python3-pyqt5 python3-construct python3-jsonschema python3-mnemonic python3-pyelftools gcc-arm-linux-gnueabihf libc6-dev-armhf-cross gdb-multiarch

3. Build::

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

    ./speculos.py /path/to/app.elf

You can then use your left / right arrows to emulate the left and right buttons of your device.

Communicating with the device
-----------------------------

You can communicate with the emulated device using `APDUs <https://en.wikipedia.org/wiki/Smart_card_application_protocol_data_unit>`_. Speculos embbeds a TCP server (listening on ``127.0.0.1:999``) to forwards APDUs to the target app.

In this example we will use the `ledgerctl <https://github.com/LedgerHQ/ledgerctl>`_ client that you can install with ``pip``::

    pip3 install ledgerwallet

If the environment variables ``LEDGER_PROXY_ADDRESS`` and ``LEDGER_PROXY_PORT`` are set, the library ill try to use the device emulated by Speculos. For instance, the following command-line sends the APDU ``e0 c4 00 00 00`` (Bitcoin-app's APDU to request the version)::

    $ ./speculos.py /path/to/app.elf &  # First start the app in the background
    $ echo 'e0c4000000' | LEDGER_PROXY_ADDRESS=127.0.0.1 LEDGER_PROXY_PORT=9999 ledgerctl send -
    10:01:09.546:apdu: > e0c4000000
    10:01:09.547:apdu: < 6d00
    6d00

Other clients are available (ledgerblue, btchip-python...) and you will find more information in `speculos' doc <https://github.com/LedgerHQ/speculos/blob/master/doc/usage.md#clients>`_.

Debugging with GDB
------------------

Speculos can also be used to debug your code with GDB::

    ./speculos.py -d /path/to/app.elf &
    ./tools/debug.sh /path/to/app.elf

This command should start a brand new gdb instance with your app already loaded !

Debugging inside Visual Studio Code
-----------------------------------

Visual Studio Code users might be happy to learn that debugging through the usual VSCode interface is made possible using speculos.

In your ``.vscode`` file, simply create a ``launch.json`` file containing this::

    {
        "version": "0.2.0",
        "configurations": [
            {
                "type": "gdb",
                "request": "attach",
                "name": "Attach to gdbserver",
                "executable": "${workspaceFolder}/bin/app.elf",
                "target": ":1234",
                "remote": true,
                "cwd": "${workspaceFolder}",
                "valuesFormatting": "parseText",
                "gdbpath": "gdb-multiarch",
                "autorun": [
                    "set architecture arm",
                    "handle SIGILL nostop pass noprint",
                    "add-symbol-file ${workspaceFolder}/bin/app.elf 0x40000000",
                    "b *0x40000000",
                    "c"
                ]
            }
        ]
    }

Make sure you have `Native Debug's extension <https://marketplace.visualstudio.com/items?itemName=webfreak.debug>`_ installed.
Then, follow these steps:


1. Set a breakpoint (click on the left-hand side of the line you want to set a breakpoint on).
2. In a new terminal, attach speculos (run ``./speculos.py -d /path/to/app.elf``).
3. In VSCode, press F5 to start the debugging session. You're good to go !

If your device is in a loop (if you get the error ``Cannot execute this command while the selected thread is running``), then you probably need to send an APDU to the device to actually reach the breakpoint you've set. Please refer to the `Communicating with the device`_ section.
