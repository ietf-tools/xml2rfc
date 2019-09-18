
==============================================================================
	     Datatracker Development in a Docker Container (beta)
==============================================================================


Intro
=====

Docker_ is a toolkit which lets you package software together with its
dependencies in lightweight containers, and run it in isolated virtual
environments.

During and just after IETF-94 I've spent quite a bit of time setting up a
docker image which provides the dependencies needed to run the datatracker,
and it's now available for beta testing.  Hopefully this should make it
substantially easier to get started with datatracker development.

Steps
=====

1. Set up Docker on your preferred platform.  Official installers exist for
   many Linux flavours, OS X, Windows and Cloud services.  Here's the full `List
   of Installation Instructions`_.

   Docker containers require the services of an underlying Linux API, which
   means that on OS X and Windows, these have to be provided by a virtual
   machine which runs a minimal Linux image.  The virtual machine used on
   non-Linux platforms is commonly VirtualBox.  On Linux kernels with version
   3.8 or later, no virtual machine is needed, as the docker images can be
   fully supported with the native kernel services.

   Please follow the Docker installations all the way through to successfully
   running the ``hello-world`` example in a terminal window ( ``$ docker run
   hello-world``).


2. Check out your datatracker branch as usual, in a suitable directory.
   We'll assume ``~/src/dt/`` here, and assume you are ``'coder'``::

      ~/src/dt/ $ svn co https://svn.tools.ietf.org/svn/tools/ietfdb/personal/coder/6.8.2.dev0

4. In the ``docker/`` directory you'll also find a wrapper script named
   ``'run'``.  We will be using the wrapper to run a pre-built docker image
   fetched from the docker hub::

      ~/src/dt/6.8.2.dev0/ $ docker/run

   This will pull down the latest docker image, set up a python virtualenv for
   you, install some dependencies, and drop you in a bash shell where you can
   run the datatracker.

6. You are now ready to run the tests::

      (virtual) $ ietf/manage.py test --settings=settings_sqlitetest

   and then start the dev server::

      (virtual) $ ietf/manage.py runserver 0.0.0.0:8000

   Note the IP address ``0.0.0.0`` used to make the dev server bind to all
   addresses.  The internal port 8000 has been mapped to port 8000 externally,
   too.  In order to find the IP address of the VirtualBox, run ``'$
   docker-machine ip'`` *outside* the virtual environment::

      ~/src/dt/6.8.2.dev0/ $ docker-machine ip
      192.168.59.103

      ~/src/dt/6.8.2.dev0/ $ open http://192.168.59.103:8000/

..  _Docker: https://www.docker.com/
..  _`List of Installation Instructions`: https://docs.docker.com/v1.8/installation/
..  _VirtualBox: https://www.virtualbox.org/


