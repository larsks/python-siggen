import os
import subprocess
import tempfile
import logging

LOG = logging.getLogger(__name__)


def run_script(s, cval=None):
    if not cval:
        return

    LOG.debug('running external script')
    sf = tempfile.NamedTemporaryFile()
    sf.write(s)
    sf.seek(0)

    os.chmod(sf.name, 0700)
    sf.file.close()
    subprocess.call([sf.name])
