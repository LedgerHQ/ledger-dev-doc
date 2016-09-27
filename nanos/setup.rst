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

.. _Ledger shop: https://www.ledgerwallet.com
.. _ROPI support: http://infocenter.arm.com/help/index.jsp?topic=/com.arm.doc.dui0491i/CHDCDGGG.html
.. _blue-devenv: https://github.com/LedgerHQ/blue-devenv/blob/master/README.md
.. _docker is installed: https://docs.docker.com/engine/installation