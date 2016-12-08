"""MyAir device discovery."""
import socket
import threading
import xml.etree.ElementTree as ElementTree

from .util import etree_to_dict

# pylint: disable=unused-import, import-error, no-name-in-module
try:
    # Py2
    from urlparse import unquote  # noqa
except ImportError:
    # Py3
    from urllib.parse import unquote  # noqa

from datetime import datetime, timedelta

UDP_SRC_PORT = 3001
UDP_DST_PORT = 3001

DISCOVERY_TIMEOUT = timedelta(seconds=5)

class MyAir(object):
    """Base class to discover MyAir devices."""

    def __init__(self):
        """Initialize the MyAir discovery."""
        self.entries = []
        self._lock = threading.RLock()

    def scan(self):
        """Scan the network."""
        with self._lock:
            self.update()

    def all(self):
        """Scan and return all found entries."""
        self.scan()
        return self.entries

    def update(self):
        """Scan network for MyAir devices."""
        entries = []

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(DISCOVERY_TIMEOUT.seconds)
        sock.bind(("", UDP_SRC_PORT))

        stop_wait = datetime.now() + DISCOVERY_TIMEOUT

        try:

            while True:
                time_diff = stop_wait - datetime.now()
                seconds_left = time_diff.total_seconds()
                if seconds_left <= 0:
                    break
                try:
                    data, (address, _) = sock.recvfrom(1024)

                    try:
                        tree = ElementTree.fromstring(data)
                        entry = (etree_to_dict(tree).get('iZS10.3').get('system'))

                    except ElementTree.ParseError:
                        logging.getLogger(__name__).error(
                            "Found malformed XML at %s: %s", url, xml)

                    except AttributeError:
                        continue

                    # expecting ip, port, name, key
                    if 'name' not in entry:
                        continue

                    if 'ip' not in entry:
                        continue

                    if 'port' not in entry:
                        continue

                    if 'key' not in entry:
                        continue

                    new_entry = {
                        'name': entry['name'].encode("UTF-8"),
                        'ip': entry['ip'],
                        'port': entry['port'],
                        'key': entry['key'].encode("UTF-8"),
                    }
                    if new_entry not in entries:
                        entries.append(new_entry)

                except socket.timeout:
                    break

        finally:
            sock.close()

        self.entries = entries


def main():
    """Test MyAir discovery."""
    from pprint import pprint
    myair = MyAir()
    pprint("Scanning for MyAir devices..")
    myair.update()
    pprint(myair.entries)


if __name__ == "__main__":
    main()
