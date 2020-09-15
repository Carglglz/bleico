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

To enable logging to a file use ``-dflev`` option with logging level required.

Freeze with Pyinstaller
-----------------------

MacOS
^^^^^
Unde ``bleico_app`` directory shell scripts
bleico_macos.spec

./clean_prev

./freeze_app

Copy ``dmg_sign_verify.sh``, ``dmg-background.png`` and ``dmg-background@2x.png``
into dist

cd into dist
[CHANGE icon manually]

Make .dmg and sign with pgp key (needs appdmg and gpg available in $PATH)
(requirements)
./dmg_sign_verify

Linux
^^^^^
Not available yet

Windows
^^^^^^^
Not available yet
