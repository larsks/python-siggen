import time
import pyaudio
import threading
import Queue as queue

CHUNK = 1024
CHANNELS = 1
RATE = 44100
WIDTH = 4
SILENCE = chr(0) * CHUNK * CHANNELS * WIDTH
BUFLEN = 1024


class Reader(threading.Thread):
    def __init__(self, stream, q):
        super(Reader, self).__init__()

        self.stream = stream
        self.q = q
        self.quit = threading.Event()

    def run(self):
        while not self.quit.is_set():
            data = self.stream.read(CHUNK)
            self.q.put(data)


class Writer(threading.Thread):
    def __init__(self, stream, q):
        super(Writer, self).__init__()

        self.stream = stream
        self.q = q
        self.quit = threading.Event()

    def run(self):
        while not self.quit.is_set():
            try:
                data = self.q.get_nowait()
            except queue.Empty:
                data = SILENCE

            self.stream.write(data)


pa = pyaudio.PyAudio()
istream = pa.open(rate=RATE,
                 input=True,
                 format=pyaudio.get_format_from_width(WIDTH),
                 frames_per_buffer=BUFLEN,
                 channels=CHANNELS)
ostream = pa.open(rate=RATE,
                 output=True,
                 format=pyaudio.get_format_from_width(WIDTH),
                 frames_per_buffer=BUFLEN,
                 channels=CHANNELS)

q = queue.Queue()
w = Writer(ostream, q)
r = Reader(istream, q)

w.start()
r.start()

w.join()
r.join()
