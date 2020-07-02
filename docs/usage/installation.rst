Welcome to LogFlow's documentation!
===================================

How to install it ?

You can do it using pip, docker or pulling from Github. The recommended way is to use Docker.
Note that nvidia-docker is recommended if you plan to use GPU for the learning step.

Download from github.

.. code-block:: bash

    python3.6 mail.py

.. code-block:: python3

    for dir in listdir(path_logs):
        if "2018" in dir:
            if not isfile(path_logs + dir):
                for file in listdir(path_logs + dir):
                    if "m1" in file or "m2" in file:
                        list_files.append(path_logs + dir + "/" + file)