Getting Started
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

Setting up the SDK
------------------

Now that you have your toolchain set up, you need to download / clone the SDK
for the appropriate Ledger device you're working with.
Make sure you checkout the tag matching your firmware version.

Ledger Nano S SDK: https://github.com/LedgerHQ/nanos-secure-sdk

Ledger Nano X SDK: https://github.com/LedgerHQ/nanox-secure-sdk

Ledger Blue SDK: https://github.com/LedgerHQ/blue-secure-sdk


Finally, link the environment variable ``BOLOS_SDK`` to the SDK you downloaded.
When using the Makefile for our BOLOS apps, the Makefile will use the contents
of the SDK to determine your target device ID (Ledger Nano S, X or Ledger Blue).
Even if you aren't building an app, loading an app with the Makefile still
requires you to have the SDK for the appropriate device linked to by
``BOLOS_SDK``.

Python Loader
-------------

If you intend to communicate with an actual Ledger device from a host computer
at all, you will need the Python loader installed. For more information on
installing and using the Python loader, see :doc:`python-loader:index`. The
Makefiles for most of our apps interface with the Python loader directly, so if
you only need to load / delete apps then you don't need to know how to use the
various scripts provided by the Python loader, but you'll still need it
installed.

Building and Loading Apps
-------------------------

In this section, we'll walk you through compiling and loading your first BOLOS
app onto your device. Applications that support multiple BOLOS devices are
typically contained within a single repository, so you can use the same
repository to build an app for different Ledger devices. Just make sure that
you've set ``BOLOS_SDK`` to the appropriate SDK for the device you're using. The
Makefiles used by our apps use the contents of the SDK to determine which device
you're using.

Firstly, download the boilerplate app.

.. code-block:: bash

   git clone https://github.com/LedgerHQ/ledger-app-boilerplate.git

Now you can let the Makefile do all the work. The ``load`` target will build the
app if necessary and load it onto your device over USB.

.. code-block:: bash

   cd ledger-app-boilerplate/
   make load

And you're done! After confirming the installation on your device, you should
see an app named "Boilerplate". The app can be deleted like so:

.. code-block:: bash

   make delete
   
The `Sia` app is a very well documented app from community. If you want to study a full fledged app, this is the one you should read:

.. code-block:: bash

   git clone https://github.com/LedgerHQ/ledger-app-sia.git
