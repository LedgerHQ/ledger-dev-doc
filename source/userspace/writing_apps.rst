Writing Apps
============

Not much documentation has been written yet (work in progress!) regarding the exact steps to follow to write apps. However, very good codebases are available for you to learn from.

* The `app-boilerplate <https://github.com/LedgerHQ/ledger-app-boilerplate.git>`_ is a thoroughly documented app that was specifically designed for developers to play around with and read the code.
* The `app-sia <https://github.com/LedgerHQ/app-sia.git>`_ is also a thoroughly documented app written by the community. If you wish to study a fully-fledged app, this is the one for you!

Cloning and Making
------------------

Applications that support multiple BOLOS devices are
typically contained within a single repository, so you can use the same
repository to build an app for different Ledger devices. Just make sure that
you've set ``BOLOS_SDK`` to the appropriate SDK for the device you're using. The
Makefiles used by our apps use the contents of the SDK to determine which device
you're using.

First, download the boilerplate app.

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
   
Display Management
------------------

The doc covered the art of displaying information on screen, go and check it out: :doc:`Display Management </userspace/display_management>`