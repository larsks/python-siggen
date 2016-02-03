# System configuration

## Systemd units

This directory contains two [systemd units][unit] which I use to
automatically start [siggen][] when my system boots.  You should
install these files in `/etc/systemd/system`.

[unit]: http://www.freedesktop.org/software/systemd/man/systemd.unit.html
[siggen]: http://github.com/larsks/python-siggen/

The `jackd.service` unit will start `jackd` (as the `synth` user) with
its own [dbus][] session through the use of the [dubs-run-session][]
command.  This unit does not need to be enabled because it will be
started on demand by the `siggen` service.

[dbus-run-session]: http://dbus.freedesktop.org/doc/dbus-run-session.1.html
[dbus]: http://www.freedesktop.org/wiki/Software/dbus/

The `siggen.service` unit will start `siggen` as the synth user.  This
unit requires the `jackd` service, which will be started automatically
if you `systemctl start siggen`.  If you want `siggen` to start
automatically, you will need to enable the service:

    systemctl enable siggen

## ALSA configuration

In order to make my USB sound card the default device, I created
`/etc/modprobe.d/alsa.conf` with the following contents:

    blacklist snd_bcm2835

This prevents the kernel from loading drivers for the built-in sound
hardware, which makes the USB sound card the default.
