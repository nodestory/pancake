pancake
=======
.. image:: https://codeship.com/projects/b9987b60-8e77-0132-3248-6a5ca7220068/status
    :target: https://codeship.com/projects/60954)

The following service dependencies need to be installed:
 * MongoDB
 * Redis-Server

To install python dependencies for development::

    make config-develop

To run tests::

    make test

To run the server::

    python pancacke/app.py

This runs the server at http://localhost:8080. Part of the API docs can be
found at http://localhost:8080/docs. Note only the following endpoints have
correct documentation there right now:
 * `/contact`
 * `/media`
 * `/event`
 * `/subscription`

The rest are erroneous due to bugs in the `Eve-Doc` library which generated
them..

Admin interface is available at http://localhost:8080/admin , no auth required.

Additional documentation can be built by running::

    make docs
