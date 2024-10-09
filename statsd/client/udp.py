import socket
import time

from .base import StatsClientBase, PipelineBase


class Pipeline(PipelineBase):

    def __init__(self, client):
        super().__init__(client)
        self._maxudpsize = client._maxudpsize

    def _send(self):
        data = self._stats.popleft()
        while self._stats:
            # Use popleft to preserve the order of the stats.
            stat = self._stats.popleft()
            if len(stat) + len(data) + 1 >= self._maxudpsize:
                self._client._after(data)
                data = stat
            else:
                data += '\n' + stat
        self._client._after(data)


class StatsClient(StatsClientBase):
    """A client for statsd."""

    def __init__(self, host='localhost', port=8125, prefix=None,
                 maxudpsize=512, ipv6=False,
                 send_retries=2, send_retry_interval=0.01, send_retry_before_callback=None,
                 send_fail_callback=None):
        """Create a new client."""
        self._ipv6 = ipv6
        self._host = host
        self._port = port
        self._addr = None
        self._sock = None
        self._prefix = prefix
        self._maxudpsize = maxudpsize
        self._send_retries = send_retries
        self._send_retry_interval = send_retry_interval
        self._send_retry_before_callback = send_retry_before_callback
        self._send_fail_callback = send_fail_callback

        self.connect()

    def connect(self):
        fam = socket.AF_INET6 if self._ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(
            self._host, self._port, fam, socket.SOCK_DGRAM)[0]
        self._addr = addr
        self._sock = socket.socket(family, socket.SOCK_DGRAM)

    def _send(self, data):
        """Send data to statsd."""
        try_count = 1
        while try_count <= self._send_retries:
            try:
                self._sock.sendto(data.encode('ascii'), self._addr)
                break
            except (OSError, RuntimeError, AttributeError) as e:
                if self._send_retry_before_callback is not None:
                    self._send_retry_before_callback(try_count, e)
                time.sleep(self._send_retry_interval)
                # reconnect
                self.close()
                try:
                    self.connect()
                except Exception as e:
                    pass

                try_count += 1
                # retry count meets the max count
                if try_count > self._send_retries and self._send_fail_callback is not None:
                    self._send_fail_callback(try_count, e)

    def close(self):
        if self._sock and hasattr(self._sock, 'close'):
            self._sock.close()
        self._sock = None

    def pipeline(self):
        return Pipeline(self)
