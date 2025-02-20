import socket
import time

from .base import StatsClientBase, PipelineBase


class StreamPipeline(PipelineBase):
    def _send(self):
        self._client._after('\n'.join(self._stats))
        self._stats.clear()


class StreamClientBase(StatsClientBase):
    def connect(self):
        raise NotImplementedError()

    def close(self):
        if self._sock and hasattr(self._sock, 'close'):
            self._sock.close()
        self._sock = None

    def reconnect(self):
        self.close()
        self.connect()

    def pipeline(self):
        return StreamPipeline(self)

    def _do_send(self, data):
        self._sock.sendall(data.encode('ascii') + b'\n')


class TCPStatsClient(StreamClientBase):
    """TCP version of StatsClient."""

    def __init__(self, host='localhost', port=8125, prefix=None,
                 timeout=None, ipv6=False,
                 send_retries=1, send_retry_interval=0.01, send_retry_before_callback=None,
                 send_fail_callback=None):
        """Create a new client."""
        self._host = host
        self._port = port
        self._ipv6 = ipv6
        self._timeout = timeout
        self._prefix = prefix
        self._sock = None
        self._send_retries = send_retries
        self._send_retry_interval = send_retry_interval
        self._send_retry_before_callback = send_retry_before_callback
        self._send_fail_callback = send_fail_callback

    def connect(self):
        fam = socket.AF_INET6 if self._ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(
            self._host, self._port, fam, socket.SOCK_STREAM)[0]
        self._sock = socket.socket(family, socket.SOCK_STREAM)
        self._sock.settimeout(self._timeout)
        self._sock.connect(addr)

    def _send(self, data):
        """Send data to statsd."""
        if not self._sock:
            self.connect()
        try_count = 1
        while try_count <= self._send_retries:
            try:
                self._do_send(data)
                break
            except (OSError, RuntimeError, AttributeError) as e:
                if self._send_retry_before_callback is not None:
                    self._send_retry_before_callback(try_count, e)
                time.sleep(self._send_retry_interval)
                # reconnect
                self.close()
                try:
                    self.connect()
                except Exception as ec:
                    pass

                try_count += 1
                # retry count meets the max count
                if try_count > self._send_retries and self._send_fail_callback is not None:
                    self._send_fail_callback(try_count, e)


class UnixSocketStatsClient(StreamClientBase):
    """Unix domain socket version of StatsClient."""

    def __init__(self, socket_path, prefix=None, timeout=None):
        """Create a new client."""
        self._socket_path = socket_path
        self._timeout = timeout
        self._prefix = prefix
        self._sock = None

    def connect(self):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.settimeout(self._timeout)
        self._sock.connect(self._socket_path)

    def _send(self, data):
        """Send data to statsd."""
        if not self._sock:
            self.connect()
        self._do_send(data)
