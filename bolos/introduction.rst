Introduction
============

The purpose of this document is to explain with multiple levels of details the architecture of applications running over BOLOS, Ledger Secure Operating System.  The document is meant to let developers dive into the BOLOS model, and give them common patterns and guidelines to avoid being lost when reviewing existing applications.

About
-----

BOLOS stands for Blockchain Open Ledger Operating System. It is an embedded secure OS, built to run on different flavors of secure hardware, such as Secure Elements, Hardware Security Modules or CPU enclave (TEE, Intel SGX).

Skill Requirements
------------------

* All applications are written in C.
* Although link scripts are fixed, makefiles can be customized at will. 
* Python scripts are used to perform administration of devices.