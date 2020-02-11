BOLOS Features
==============

In this section, we'll discuss some of the features that are built into BOLOS.
These features are available through the :ref:`dashboard app <dashboard>` and /
or can be utilized by userspace applications.

Management of Cryptographic Secrets
-----------------------------------

There are two important cryptographic secrets that are stored and managed by
BOLOS that will be discussed in this section: the :term:`Device` keypair (which
is generated in-factory) and the :doc:`BIP 32 master node
</background/master_seed>` (which is derived from the user's BIP 39 mnemonic
seed). Both of these secrets are stored by BOLOS and are not directly accessible
to applications for security reasons. The Device keypair can be used indirectly
by applications for purposes of :ref:`application attestation <endorsement>`.
Applications can derive secrets from the BIP 32 master node using a system call
to BOLOS, provided the app was given the appropriate permissions when loaded
onto the device.

Passphrases in BOLOS
^^^^^^^^^^^^^^^^^^^^

Since firmware version 1.3 on the Ledger Nano S, BOLOS allows users to load
multiple `BIP 39 passphrases
<https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki#from-mnemonic-to-seed>`_
onto the device at once. As described in :doc:`the previous chapter
</background/master_seed>`, passphrases are a method to add additional entropy
to the BIP 39 master seed in order to completely change the :doc:`HD tree
</background/hd_keys>`. Users can set a temporary passphrase which is activated
until the device is disconnected, or store a passphrase on the device by
attaching it to a PIN. When a passphrase is attached to a PIN, it is only
activated when the user unlocks the device using the PIN corresponding to that
passphrase. See our `Help Center article on the advanced passphrase options
<https://support.ledger.com/hc/en-us/articles/115005214529-Advanced-passphrase-security>`_
for more information about using passphrases.

When a passphrase is activated, the binary seed derived according to BIP 39 is
changed and as such the entire HD tree is changed. This means that using a
different passphrase causes applications that derive information from the HD
tree (like cryptocurrency wallet applications) to derive entirely different
information (different cryptocurrency addresses will be generated).

Attestation
-----------

Attestation is a process used by Ledger devices to prove that they are a genuine
Ledger device, and not a knock-off or fake version. It can be used by BOLOS when
connecting to a host computer to prove that the device has not been tampered
with. It can also be used by applications to prove that they are running on a
genuine Ledger device. BOLOS also supports endorsement of the device by third
parties (called :term:`Owners <Owner>`) for attestation purposes.

.. _anti-tampering:

Anti-Tampering with Attestation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: images/wallet_not_genuine.png
   :align: center

Ledger devices are protected from interdiction attacks (being tampered with
while en route from Ledger's warehouses to your home) due to anti-tampering
technology built into the firmware. Using attestation, the authenticity of the
device is verified in software every time you plug it into one of the Ledger
Chrome applications.

When all Ledger devices are provisioned in the factory, they first generate a
unique :term:`Device` public-private keypair. The Device's public key is then
signed by Ledger's :term:`Issuer` key to create an Issuer Certificate which is
stored in the device. This certificate is a digital seal of authenticity of the
Ledger device. By providing the Device's public key and Issuer Certificate, the
device can prove that it is a genuine Ledger device.

When the Ledger device connects to one of the Ledger Chrome applications, the
device uses the Issuer Certificate to prove that it is an authentic device (this
takes place during establishment of the :ref:`Secure Channel <secure-channel>`,
as we'll discuss later in this section). If an attacker created a clone of the
device running rogue firmware, this attestation process would fail and the
device would be rejected as non-genuine. It is impossible for an attacker to
replace the firmware on the device and have it pass attestation without having a
Device private key and the corresponding Issuer Certificate, signed by Ledger.

It is incredibly unlikely for the Device private key to become compromised,
because the Secure Element is designed to be a stronghold against such physical
attacks. It is theoretically possible to extract the private key, but only with
great expense and time, so only an organization such as the NSA could do it.

.. tip::

   For more information about the benefits of Ledger's use of a Secure Element
   for verifying device authenticity, see our blog post `How to protect hardware
   wallets against tampering
   <https://www.ledger.com/how-to-protect-hardware-wallets-against-tampering/>`_
   (though keep in mind that not all of the information in this article applies
   to Ledger's latest products).

.. _endorsement:

Endorsement & Application Attestation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As discussed in the previous subsection, the :term:`Device` private key can be
used to prove authenticity of a Ledger device. However, direct access to the
device private key is limited to BOLOS, so it can't be directly utilized by
individual applications on the device (to avoid compromising the key). However,
applications can indirectly use the Device private key for attestation purposes
by generating attestation keypairs.

Attestation keypairs can be generated on demand by the user for applications to
use. An attestation key can be setup using the :ref:`endorsementSetup.py` or
:ref:`endorsementSetupLedger.py` Python loader scripts. When generating an
attestation keypair, the host computer connects to the dashboard application and
initiates a :ref:`Secure Channel <secure-channel>` before instructing the device
to create an attestation keypair. The device generates a new attestation keypair
and signs it using the :term:`Device` private key to create a Device
Certificate. The device then returns the attestation public key, the Device
Certificate, and the Issuer Certificate over the Secure Channel to the host. The
host, which may be Ledger or a third party, then signs the attestation public
key with an :term:`Owner` private key, thus creating an Owner Certificate which
is sent back over the Secure Channel and stored by the device (in this way, the
Owner "endorses" the authenticity of the device). The device can then prove that
the attestation key belongs to a genuine Ledger device using the Device
Certificate and the Issuer Certificate, and that the attestation key is trusted
by the Owner using the Owner Certificate.

The attestation keys are not accessible to apps directly, instead BOLOS provides
attestation functionality to userspace applications through cryptographic
primitives available as system calls. There are two different Endorsement
Schemes available to applications (Endorsement Scheme #1 and Endorsement Scheme
#2). When creating an attestation keypair, the user must choose which scheme the
keypair shall belong to. Applications can then use that keypair by using the
cryptographic primitives offered for the appropriate Endorsement Scheme.

Endorsement Scheme #1 offers two cryptographic primitives:

``os_endorsement_key1_get_app_secret(...)``
   Derive a secret from the attestation private key and the hash of the running
   application.

``os_endorsement_key1_sign_data(...)``
   Sign a message concatenated with the hash of the running application using
   the attestation private key (this signature can be verified using
   :ref:`verifyEndorsement1.py`).

Endorsement Scheme #2 offers a single cryptographic primitive:

``os_endorsement_key2_derive_sign_data(...)``
   Sign a message using a private key derived from the attestation private key
   and the hash of the running application (this signature can be verified using
   :ref:`verifyEndorsement2.py`).

For an example of how these features may be used, check out `blue-app-otherdime
<https://github.com/LedgerHQ/blue-app-otherdime>`_ and `this blog post
<https://blog.ledger.co/attestation-redux-proving-code-execution-on-the-ledger-platform-fd11ab0f7c19>`_
which discusses the app in detail.

Attestation Chain of Trust
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: images/chain_of_trust.png
   :align: center

   The chain of trust for Ledger's attestation model

This diagram shows the chain of trust of our attestation model. All data signed
by the attestation keys can be trusted to have been signed by an authentic
Ledger device. This is because the Device Certificate is proof that the
attestation keys belong to a device, and the Issuer Certificate is proof that
the device is genuine. Additionally, the Owner Certificate is proof that the
attestation keys are trusted by Owner (which may be Ledger or a third party).

.. _secure-channel:

Secure Channel
--------------

Throughout the standard device lifecycle, it is possible for a host computer to
establish a Secure Channel with a device to verify its authenticity and to
securely exchange secrets with it.

As discussed in :ref:`anti-tampering`, the authenticity of a Ledger device can
be verified when it connects to a host computer by requesting the device's
:term:`Issuer Certificate`, which is signed by Ledger. This is done when
establishing a Secure Channel with the device. However, the Secure Channel is
not only a means to verify the authenticity of a Ledger device, it also allows
the host computer to establish an encrypted communication channel with the
device. Only the :ref:`dashboard application <dashboard>` is able to establish a
Secure Channel with the host computer, as doing so requires access to the
:term:`Device` private key.

The Secure Channel protocol is built on top of the APDU protocol used to
communicate with the device over USB. As such, the protocol consists of a series
of Command APDUs being sent from the host computer, and then associated Response
APDUs being sent back from the device, with a one-to-one correspondence. The
Secure Channel exists between two parties: the Signer and the Device. The Signer
is the remote host connecting to the device. This may be the Issuer (Ledger)
connecting to the device through our APIs, a :term:`Custom Certificate Authority
<Custom CA>` connecting to the device using a previously :ref:`enrolled Custom
CA public key <custom-ca-enrollment>`, or another end-user using a randomly
generated keypair.

When establishing the Secure Channel, both parties (the Signer and the Device)
generate an ephemeral keypair which is later used to calculate a shared secret
using ECDH for encrypted communications between the two parties. Both parties
prove that they trust their respective ephemeral public keys by each providing a
certificate chain. These certificate chains incorporate both a Signer nonce and
a Device nonce to avoid reuse of the certificates by an eavesdropper. If the
root certificate in the certificate chain provided by the Signer is signed by a
party that is trusted by the device, then the device grants the remote host
special permissions after establishing the Secure Channel. For example, if the
root certificate in the Signer's certificate chain is signed by a previously
enrolled Custom CA keypair or Ledger's Issuer keypair, then the host can add or
remove apps from the device without the user's confirmation.

The process of establishing a Secure Channel is illustrated in the following
diagram.

.. figure:: images/secure_channel_protocol.png
   :align: center

   An admittedly not-so-simple diagram of the Secure Channel protocol handshake

In the above diagram, during segment (6), the Device provides a Signer serial.
The Signer serial is a number stored by the device which identifies the specific
Issuer keypair used to sign the device's Issuer Certificate, as Ledger does not
use the same Issuer keypair for every device.

The Signer certificate chain is generated, sent to the device, and verified from
(7) to (11). The Device certificate chain is generated, sent to the Signer, and
verified from (12) to (16). In this example, both certificate chains consist of
two certificates. The root certificate in the Signer certificate chain is
self-signed. The final certificate in the Signer certificate chain is signed by
the Signer and verifies the authenticity of the Signer ephemeral public key. The
root certificate in the Device certificate chain is the Issuer Certificate (as
such, verifying this certificate implicitly verifies the authenticity of the
device). The final certificate in the Device certificate chain is signed by the
Device and verifies the authenticity of the Device ephemeral public key.

.. _custom-ca-enrollment:

Custom CA Public Key Enrollment
-------------------------------

:term:`Custom Certificate Authorities <Custom CA>` have the option to generate a
keypair (using :ref:`genCAPair.py`) and enroll their public key onto the device
(using :ref:`setupCustomCA.py`). Enrolling the Custom CA public key onto the
device gives them the following special privileges:

* The Custom CA can open authenticated :ref:`Secure Channels <secure-channel>`
  with the device (using the ``--rootPrivateKey`` option of the Python loader
  scripts).
* The Custom CA can sign applications (using :ref:`signApp.py`) to create a
  signature which can be used to avoid the user confirmation when loading the
  app on the device.

This feature may be used by BOLOS application developers to simplify the
development process, but it is intended to be much wider in scope than that.
This feature may also be used by third party companies to give their own
application manager permissions to manage the device without needing user
confirmation on every action.

Parties Involved in our Model
-----------------------------

Below is a definition of all of the parties involved in our public key
cryptography model.

.. glossary::

   Device
   Device Certificate
      The meaning of this term should be quite self-evident, however in our
      public key cryptography model it has a distinct meaning. Each Device has a
      **unique** public-private keypair that is known **only to that device**.
      In the factory, the Device generates it's own public-private keypair. The
      Device's private key is not known by Ledger. The Device public-private key
      pair can be used to sign certificates.

   Issuer
   Issuer Certificate
      The Issuer is the party that initially provisions the :term:`Device`. This
      party is always Ledger. The Issuer has a public-private keypair that can
      be used to sign Issuer Certificates. Note that Ledger uses multiple Issuer
      keypairs, not just one.

   Owner
   Owner Certificate
      An Owner is simply a party that owns and / or verifies the authenticity of
      a Ledger device. An Owner has a public-private keypair that can be used to
      sign certificates. A single :term:`Device` can have zero or more Owners,
      and the Owner doesn't have to be Ledger. The device uses Owner
      Certificates exclusively for the purposes of :ref:`application attestation
      <endorsement>`.

   Custom CA
   Custom CA Certificate
      A Custom Certificate Authority has a public-private keypair, where the
      public key is :ref:`enrolled on the device <custom-ca-enrollment>`. The
      Custom CA's private key can then be used to establish authenticated
      :ref:`Secure Channels <secure-channel>` with the device and sign
      applications.

      A Custom CA may be a BOLOS application developer or a third party company
      that would like to give their application manager special administration
      permissions with a BOLOS device.
