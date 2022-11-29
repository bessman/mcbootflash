Library API
===========

When mcbootflash is used as a library, the main object of intereset is the
:class:`~mcbootflash.connection.BootloaderConnection`. It provides methods for
flashing new firmware, erasing existing firmware, reading metadata from the
connected device, and resetting the device.

The :mod:`~mcbootflash.flashing` module also offers a command-line interface
which other applications can hook into to set their own defaults, add or remove
parameters, set help messages, etc. See :ref:`cli`.

connection
----------
.. automodule:: mcbootflash.connection
   :members:
   :undoc-members:
   :show-inheritance:

protocol
--------
See also :ref:`protocol_specification`.

.. automodule:: mcbootflash.protocol
   :members:
   :undoc-members:
   :show-inheritance:


flashing
--------
See also :ref:`cli`.

.. automodule:: mcbootflash.flashing
   :members:
   :undoc-members:
   :show-inheritance:
      
error
-----
.. automodule:: mcbootflash.error
   :members:
   :undoc-members:
   :show-inheritance:

