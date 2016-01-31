class SynthError(Exception):
    pass


class BootFailed(SynthError):
    pass


class MissingDevice(SynthError):
    pass


class MissingPAInputDevice(MissingDevice):
    pass


class MissingPAOutputDevice(MissingDevice):
    pass


class MissingPMInputDevice(MissingDevice):
    pass


class AlreadyListening(SynthError):
    pass


