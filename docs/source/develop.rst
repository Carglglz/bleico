Develop
=======

Contribute
----------
Feel free to clone or fork and commit to develop branch, contributions are welcome.


- `Issue Tracker <https://github.com/Carglglz/bleico/issues>`_.
- `Source Code  <https://github.com/Carglglz/bleico>`_.

To enhance bleico compatibility with devices that exposes custom/vendor
Characteristics have a look at
`bleak-sigspec <https://bleak-sigspec.readthedocs.io/en/latest/>`_

To enable logging to a file use ``-dflev`` option with the required
logging level.

Freeze with Pyinstaller
-----------------------

MacOS
^^^^^
Under ``bleico_app`` directory there are some shell scripts to ease freezing
bleico into a standalone application:

  - **clean_prev.sh**: To clean previous build/dist files

  - **freeze_app.sh**: To freeze bleico using pyinstaller [#]_

  - **dmg_sign_verify.sh**:
      To create a ``.dmg`` disk image, its hash SHA256 file and sign
      it with your own key using `gpg` for distribution. (needs `appdmg` [#]_
      and `gpg` [#]_ available in $PATH)


.. note::

    *freeze_app.sh* script uses ``bleico_macos.spec`` file, where the default
    python path for ``bleak_sigspec`` is:
    ``/Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7``
    Make sure to modify this if using a different python version or point it
    to the right place where ``bleak_sigspec`` is installed.

To freeze do:

.. code-block:: console

    bleico_app$ ./clean_prev
    Cleaining build and dist





    Done!

   bleico_app$ ./freeze_app
   Creating app bundle...
   84 INFO: PyInstaller: 4.0
   84 INFO: Python: 3.7.6
   95 INFO: Platform: Darwin-18.7.0-x86_64-i386-64bit
   [...]
   25746 INFO: moving BUNDLE data files to Resource directory

   Done!

Copy ``dmg_sign_verify.sh``, ``bleico.icns``, ``bleico_appdmg.json``, ``dmg-background.png`` and ``dmg-background@2x.png``
into *dist* folder (if freezing for the first time)

.. code-block:: console

    bleico_app$ cp dmg* dist/
    bleico_app$ cp bleico_appdmg.json dist/
    bleico_app$ cp bleico.icns dist/
    bleico_app$ cd dist

[CHANGE icon manually]


.. code-block:: console

    dist$ ./dmg_sign_verify
    Creating dmg...
    [ 1/21] Looking for target...                [ OK ]
    [ 2/21] Reading JSON Specification...        [ OK ]
    [ 3/21] Parsing JSON Specification...        [ OK ]
    [ 4/21] Validating JSON Specification...     [ OK ]
    [ 5/21] Looking for files...                 [ OK ]
    [...]
    Your image is ready:
    bleico_img.dmg
    Hashing...
    bleico_img.dmg: OK
    Signing with gpg key...
    gpg: assuming signed data in 'bleico_img.dmg'
    gpg: Signature made Wed Sep 16 19:05:58 2020 WEST
    gpg:                using RSA key 03645B8E539129670B4503027DBA72A2C9531DA6
    gpg: Good signature from "cgglzpgp <carlosgilglez@gmail.com>" [ultimate]

    Done!

Now the app is ready for distribution.

Linux
^^^^^
Not available yet

Windows
^^^^^^^
Not available yet


.. [#] See `Pyinstaller <https://www.pyinstaller.org>`_

.. [#] See `appdmg <https://github.com/LinusU/node-appdmg>`_

.. [#] See `gpg <https://gnupg.org/index.html>`_
