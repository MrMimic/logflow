Welcome to LogFlow's documentation!
===================================

How to install it ?

You can do it using pip, docker or pulling from Github. The recommended way is to use Docker.
Note that nvidia-docker is recommended if you plan to use GPU for the learning step.

Docker
------
Using the Dockerfile at the root of this git.

.. code-block:: bash

    docker build -t logflow .

Then, start the docker using nvidia-docker

.. code-block:: bash

    nvidia-docker run -it --pid=host -v $(pwd):/home/code logflow /bin/bash

Now, you are inside your docker

.. code-block:: bash

    cd /home/code

Create a data and a model directory

.. code-block:: bash

    mkdir data
    mkdir model

Pip
---

.. code-block:: bash

    pip install -i https://test.pypi.org/simple/ --no-cache-dir --extra-index-url=https://pypi.org/simple/ LogFlow-Atos-Marc-Platini

Note that it's a pre-alpha pip version. Usage of docker is recommended instead of pip.


Now, you are ready to use LogFlow !