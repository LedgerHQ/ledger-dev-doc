Setup
===============

.. warning::

   Only Linux is supported as a development OS. For Windows and MacOS users, a Linux VM is recommended.

Developing and / or compiling BOLOS applications requires the SDK matching the
appropriate device (the Nano S, X SDK or the Blue SDK) as well as the following two
compilers:

* A standard ARM gcc to build the non-secure (STM32) firmware and link the
  secure (ST31) applications
* A standard ARM clang above 7.0.0 with `ROPI support
  <http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0491i/CHDCDGGG.html>`_
  to build the secure (ST31) applications
* Download a prebuilt gcc from `here
  <https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads>`_

  
Setting up the Toolchain
------------------------

The Makefiles used by our BOLOS applications look for gcc and clang
installations using the ``PATH`` environment variable.

If you don't want to install specific versions of clang and gcc directly on your system,
simply prepend their location in your ``PATH`` environment variable.

.. code-block:: bash

   # GCC
   PATH=~/bolos-devenv/gcc-arm-none-eabi-5_3-2016q1/bin:$PATH

   # Clang
   PATH=~/bolos-devenv/clang+llvm-7.0.0-x86_64-linux-gnu-ubuntu-16.04/bin:$PATH


Cross compilation headers are required and provided within the gcc-multilib and g++-multilib packages.
To install them on a debian system:

.. code-block:: bash

   sudo apt install gcc-multilib g++-multilib

If you wish to load applications on your device, you will also need to add the appropriate :code:`udev` rules.

.. code-block:: bash

   wget -q -O - https://raw.githubusercontent.com/LedgerHQ/udev-rules/master/add_udev_rules.sh | sudo bash

Setting up the SDK
------------------

Now that you have your toolchain set up, you need to download / clone the SDK
for the appropriate Ledger device you're working with.
Make sure you checkout the tag matching your firmware version.

Ledger Nano S SDK: https://github.com/LedgerHQ/nanos-secure-sdk

Ledger Nano X SDK: https://github.com/LedgerHQ/nanox-secure-sdk

Ledger Blue SDK: https://github.com/LedgerHQ/blue-secure-sdk


Finally, link the environment variable ``BOLOS_SDK`` to the SDK you downloaded.

.. code-block:: bash

   BOLOS_SDK='/path/to/sdk/'

When using the Makefile for our BOLOS apps, the Makefile will use the contents
of the SDK to determine your target device ID (Ledger Nano S, X or Ledger Blue).
Even if you aren't building an app, loading an app with the Makefile still
requires you to have the SDK for the appropriate device linked to by
``BOLOS_SDK``.

Python Loader
-------------

Most apps use the Python loader, a Ledger-made Python library to communicate with Ledger devices.

To install it, you will need to add a couple of extra dependencies:

.. code-block:: bash

   sudo apt install virtualenv libudev-dev libusb-1.0-0-dev

You will also need the :code:`python-dev-tools` (aka :code:`python-dev` on Python 2) package

.. code-block:: bash

   python3 -m pip install python-dev-tools --user --upgrade
   python3 -m pip install ledgerblue

If you need more information about the Python loader, feel free to check out the github repo: https://github.com/LedgerHQ/blue-loader-python .
You should find what you're looking for in the :code:`doc` folder and :code:`README.md` .

Now that you're setup and ready to go, you can start looking at our :doc:`Writing Apps </userspace/writing_apps>` article!