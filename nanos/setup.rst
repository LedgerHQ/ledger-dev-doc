Getting started
===============

The Ledger Nano S is a personal lightweight mobile device architectured around a ST31 secure element with USB connectivity. 

It is based on BOLOS (Blockchain Open Ledger Operating System), where apps can run securely in full isolation and leverage the main secrets (BIP39 seed) through allocated derivations. 

The Nano S can be purchased from `Ledger shop`_ and resellers.

In order to build applications for the Nano S, you must first setup your development environment.

Development environment setup
-----------------------------

Developping applications for Nano S requires two compilers :

* A standard ARM gcc to build the non-secure (STM32) firmware and link the secure (ST31) applications
* A customized ARM clang with `ROPI support`_ to build the secure (ST31) applications

We are proiving the instructions using a docker environment image. If you wish to build from scratch, refer to the instructions on our `blue-devenv`_ repository. Before you continue, make sure that `docker is installed`_.

.. code-block:: shell

    docker pull nbasim/ledger-blue-sdk
    docker run -t -i nbasim/ledger-blue-sdk /bin/bash
    cd home
    git clone https://github.com/LedgerHQ/nanos-secure-sdk.git
    apt-get update
    apt-get install libc6-dev-i386

You can now compile applications from source for your Nano S. The next step is to install the Python tools to communicate with Nano S and manage applications life cycle.

It is recommended to install this package in a Virtual Environment in your native environment (not a Docker image) to avoid hidapi issues. So execute the following commands directly in your host shell:


.. code-block:: shell

    virtualenv ledger
    source ledger/bin/activate
    pip install ledgerblue


First app: Hello World
----------------------

Go back to your docker VM shell:

.. code-block:: shell

    git clone https://github.com/LedgerHQ/blue-sample-apps.git
    cd blue-sample-apps/blue-app-helloworld

Edit ``Makefile`` to configure the app to be compiled with the Nano S UI:

.. code-block:: shell

    TARGET_ID = 0x31100002 #Nano S
    #TARGET_ID = 0x31000002 #Blue

Then you can compile the app:

.. code-block:: shell

    make BOLOS_ENV=/opt/ledger-blue/ BOLOS_SDK=/home/nanos-secure-sdk

It will generate ``bin/token.hex`` which can be flashed on the Nano S using the Python tools.
Execute this command on your host environment:

.. code-block:: shell

    docker cp c731409caf59:/home/blue-sample-apps/blue-app-helloworld/bin/token.hex .

Replace ``c731409caf59`` by your own container ID (if you do not know it use ``docker ps -a`` to find it).

You can then install the application on your Nano S:

.. code-block:: shell

    python -m ledgerblue.loadApp --targetId 0x31100002 --apdu --fileName token.hex --appName Hello --appFlags 0x00 --icon ""

You will have to confirm twice on the device to authorize the installation. Once the app is installed, you can select it on the dashboard and launch it by pressing both buttons (to exit this app, also press both buttons).

If you wish to remove the app from your device:

.. code-block:: shell

    python -m ledgerblue.deleteApp --targetId 0x31100002 --appName Hello




.. _Ledger shop: https://www.ledgerwallet.com
.. _ROPI support: http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0491i/CHDCDGGG.html
.. _blue-devenv: https://github.com/LedgerHQ/blue-devenv/blob/master/README.md
.. _docker is installed: https://docs.docker.com/engine/installation
