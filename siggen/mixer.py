import pyalsa.alsamixer as alsamixer


class Mixer(object):
    def __init__(self, element, device='default'):
        self.mixer = alsamixer.Mixer()
        self.mixer.attach(device)
        self.mixer.load()
        self.element = alsamixer.Element(self.mixer, element)

    def set_volume(self, channel, pct):
        r = self.element.get_volume_range()
        v = r[0] + int((r[1]-r[0]) * pct)
        self.element.set_volume(v, alsamixer.channel_id[channel])
