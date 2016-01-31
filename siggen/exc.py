class SynthError(Exception):
    pass


class BootFailed(SynthError):
    '''This exception is raised if the PYO sound server fails to start.'''
    pass


class MissingDevice(SynthError):
    '''Subclasses of this exceptions are raised when devices specified in
    the configuration cannot be found.'''
    pass


class MissingPAInputDevice(MissingDevice):
    '''Raised if a portaudio input device is missing.'''
    pass


class MissingPAOutputDevice(MissingDevice):
    '''Raised if a portaudio output device is missing.'''
    pass


class MissingPMInputDevice(MissingDevice):
    '''Raised if as portmidi device missing.'''
    pass


class MissingALSADevice(MissingDevice):
    '''Raised if an ALSA device is missing.'''
    pass


class AlreadyListening(SynthError):
    '''Raised by register_midi_listener if a listener is already registered
    for the specified MIDI control.'''
    pass
