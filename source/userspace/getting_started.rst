Getting Started
===============

.. warning::

   Only Linux is supported as a development OS. For Windows and MacOS users, a Linux VM is recommended.

Developing and / or compiling BOLOS applications requires the SDK matching the
appropriate device (the Nano S SDK or the Blue SDK) as well as the following two
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

The Makefiles used by our BOLOS applications look for the gcc and clang
installations using the following process:

1. If the ``BOLOS_ENV`` environment variable is set, then gcc is used from
   ``$BOLOS_ENV/gcc-arm-none-eabi-5_3-2016q1/bin/`` and clang is used from
   ``$BOLOS_ENV/clang-arm-fropi/bin/``.
2. As a fallback, if ``BOLOS_ENV`` is not set, then gcc is used from ``GCCPATH``
   and clang is used from ``CLANGPATH``.
3. As a fallback, if either ``GCCPATH`` or ``CLANGPATH`` is not set, then gcc
   and clang, respectively, are used from the PATH.

This allows you to setup both gcc and clang under the same directory and
reference it using ``BOLOS_ENV``, or configure where each compiler is looked for
individually. If your system already has an appropriate version of clang
installed, you may simply leave ``BOLOS_ENV`` and ``CLANGPATH`` unset and clang
will be used from the PATH (but make sure to set ``GCCPATH``).

If you're just looking for a one-size-fits-all solution to satisfy your
toolchain needs, here are the steps you should follow:

1. Choose a directory for the BOLOS environment (I'll use ``~/bolos-devenv/``)
   and link the environment variable ``BOLOS_ENV`` to this directory.
2. Download a prebuilt gcc from
   https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads and unpack
   it into ``~/bolos-devenv/``. Make sure there is a directory named ``bin``
   directly inside ``~/bolos-devenv/gcc-arm-none-eabi-5_3-2016q1/``.
3. Download a prebuilt clang from http://releases.llvm.org/download.html#7.0.0
   and unpack it into ``~/bolos-devenv/``. Rename the directory that was inside
   the archive you downloaded to ``clang-arm-fropi``, or create a link to the
   directory with that name. Make sure there is a directory named ``bin``
   directly inside ``~/bolos-devenv/clang-arm-fropi/``.

.. note::

   Not all of the Makefiles for our applications available on GitHub may
   recognize ``BOLOS_ENV`` in the way described above. If the Makefile is having
   trouble finding the right compilers, try setting ``GCCPATH`` and
   ``CLANGPATH`` explicitly.

Cross compilation headers are required and provided within the gcc-multilib and g++-multilib packages.
To install them on a debian system:

.. code-block:: bash

   sudo apt install gcc-multilib g++-multilib

Setting up the SDK
------------------

Now that you have your toolchain set up, you need to download / clone the SDK
for the appropriate Ledger device you're working with. You can do this anywhere,
it doesn't have to be in your ``BOLOS_ENV`` directory (if you even have one).
Make sure you checkout the tag matching your firmware version.

Ledger Nano S SDK: https://github.com/LedgerHQ/nanos-secure-sdk

Ledger Blue SDK: https://github.com/LedgerHQ/blue-secure-sdk

Finally, link the environment variable ``BOLOS_SDK`` to the SDK you downloaded.
When using the Makefile for our BOLOS apps, the Makefile will use the contents
of the SDK to determine your target device ID (Ledger Nano S or Ledger Blue).
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
