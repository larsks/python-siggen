import os
import subprocess
import tempfile
import logging

LOG = logging.getLogger(__name__)


def run_script(s, cval=None):
    '''This writes the content of s to a file and executes it.  The
    `cval` parameter receives the control value from the MIDI listener; we
    check for nonzero values to avoid executing on both button
    press-and-release.'''

    if not cval:
        return

    LOG.debug('running external script')
    sf = tempfile.NamedTemporaryFile()
    sf.write(s)
    sf.seek(0)

    os.chmod(sf.name, 0700)
    sf.file.close()
    subprocess.call([sf.name])
