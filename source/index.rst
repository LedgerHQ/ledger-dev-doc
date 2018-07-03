Ledger Documentation Hub
========================

.. note::

   This documentation is intended for developers only and not general users.

Ledger produces personal security devices such as the Ledger Nano S and the
Ledger Blue, both of which are architected around a Secure Element and the BOLOS
platform.

This documentation contains information about developing apps for these devices,
from high-level concepts like hierarchical deterministic key generation to
low-level details about the hardware architecture of these devices.

.. toctree::
   :caption: Background Information
   :maxdepth: 1

   background/introduction
   background/personal_security_devices
   background/master_seed
   background/hd_keys
   background/hd_use_cases
   background/application_isolation

.. toctree::
   :caption: BOLOS Platform
   :maxdepth: 1

   bolos/introduction
   bolos/overview
   bolos/features
   bolos/hardware_architecture
   bolos/application_environment

.. toctree::
   :caption: Userspace Development
   :maxdepth: 1

   userspace/introduction
   userspace/getting_started
   userspace/syscalls
   userspace/application_structure
   userspace/display_management
   userspace/memory
   userspace/troubleshooting

.. toctree::
   :caption: Additional Resources
   :maxdepth: 1

   additional/publishing_an_app
   additional/external_docs
