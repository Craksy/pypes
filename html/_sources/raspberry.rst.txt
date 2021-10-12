=========
Raspberry
=========




What is a Raspberry Pi
----------------------

A Raspberry Pi is a pocket-sized :term:`SoC` that exposes a number of
:term:`GPIO pins<GPIO>`, and has ports for HDMI, USB and ethernet which makes
it popular both as a tinkerboard for hobbyists, but also as a minimal controller
for infoscreens and other small embedded devices in the industry.

The Raspberry Pi ships with :term:`Raspbian`, but there is an ever growing
selection of operating systems available, both other general purpose and
:term:`specialized or JeOS<JeOS>` systems that focus on everything from
server hosting, to gaming or media streaming.

Installing an operating system
------------------------------

Installing an operating system on a Raspberry Pi is incredibly simple and
straightforward. In short, all you need to do is download an :term:`Disk image`
and flash it onto the Pi’s SD-card.

There is a large number of systems to choose from. Some are specialized for a
single use case (:term:`JeOS`) while others are general purpose operating
systems. ARM variants are available for most popular Linux distributions.

.. important::

    If you download an image of a generic Linux distribution, make sure to get the
    one made for ARM-architecture. Often they can be found on the same download
    page, but the Pi obviously wont boot from a x86 image.

Here are links to a few of the most popular OSs:

- `Ubuntu <https://ubuntu.com/download/raspberry-pi>`_ (Server and Desktop)

- `Raspberry Pi OS <https://www.raspberrypi.com/software/operating-systems/>`_

- `RetroPie <https://retropie.org.uk/download/>`_

.. note::

    All of those images are also available through the Raspberry Pi
    Imager, without needing to download first (see below)


To flash the SD-card you need a flashing software. A popular choice is `Etcher <https://www.balena.io/etcher/>`_.
There is also the `Raspberry Pi Imager <https://www.raspberrypi.org/%20downloads/>`_ from the Raspberry Pi website, which aims
to be easy to use for beginners and can automatically download images for the
most common operating systems, including Raspbian and RetroPie.

After flashing the image, simply insert it into the Raspberry Pi and boot it up.

Depending on the operating system you may have to perform some first-time
configuration steps. These vary depending on the system, and you should consult the
documentation for instructions. It’s usually very straightforward though.

Setting up RetroPie
-------------------

Turning a Pi into an arcade machine or gaming system is super easy with RetroPie.
This is a brief explaination of the setup, and is mostly included for
completeness. For more detailed instructions consult the `RetroPie documentation <https://retropie.org.uk/docs/>`_.
It’s very comprehensive and easy to understand.

The operating system works out of the box with no additional installation or
configuration required aside from setting up controllers and adding games.

Adding games
~~~~~~~~~~~~

Games are added in the form of :term:`ROM-files<ROM>` which can be loaded
into the various emulators installed on the RetroPie.
There are several websites where ROMs can downloaded for free.

There’s a few options for adding them to the Pi, but the easiest is to transfer using a USB flash drive:

- First format the drive to FAT32

- Create an empty folder called ``retropie``

- Put it in the Pi and wait for a moment. RetroPie will create the folder structure in which ROMS are organized.

- Put it back into your PC and copy your ROMs into their respective consoles folder.

- Put the flash drive back into the Pi. Wait a few minutes for it to transfer
  the files. If you have a bunch of files, give it a bit longer.

- Reload the game list by pressing the ``Start`` button and selecting **Quit -> Restart Emulation**
