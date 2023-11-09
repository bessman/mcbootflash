.. module:: mcbootflash.protocol
    :noindex:	    

.. _protocol_specification:
       
Protocol specification
======================

Communication between mcbootflash and a connected bootloader is split up into
discrete :class:`packets <mcbootflash.protocol.Packet>`. The layout of a basic
packet is as follows:

.. autoclass:: Packet
   :noindex:

Every packet sent to or from the bootloader has at least these four fields.

The bootloader never sends anything without first receiving a packet from
the host application. After receiving a command packet, the bootloader must
respond with exactly one packet in return. The response packet's `command`
field must be the same as that of the received command packet.

Command packets
---------------

Packets sent from the host application to the bootloader are called command
packets. They have the same data layout as the basic packet specified above,
plus an optional `data` field following the `address` field. The following
commands are supported:

.. autoclass:: CommandCode
    :members:
    :undoc-members:
    :noindex:

Response packets
----------------

Replies from the bootloader come in two variations; responses to `READ_VERSION`
and responses to other commands. Responses to `READ_VERSION` have the following
format:

.. autoclass:: Version
    :noindex:

Responses to all other commands have the following basic layout:

.. autoclass:: Response
    :noindex:

The `success` field has one of the following values:

.. autoclass:: ResponseCode
    :members:
    :undoc-members:
    :noindex:

Some commands (`GET_MEMORY_ADDRESS_RANGE` and `CALCULATE_CHECKSUM`) send
additional data following the `success` field:

.. autoclass:: MemoryRange
    :noindex:

.. autoclass:: Checksum
    :noindex:

Program flowchart
-----------------

Blue arrows/bubbles indicate normal program flow, red arrows/bubbles indicate
errors.
       
.. image:: _static/session.gif

.. note::

  \* If SELF_VERIFY returns SUCCESS immediately after an ERASE_FLASH command, the
  erase failed. Normal execution flow therefore requires a response of
  VERIFY_FAIL.
