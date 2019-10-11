import machine
import usocket

class Response:

    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)


def request(method, url, data=None, json=None, headers={}, stream=None):
    perf = machine.Timer.Chrono()
    perf.start()

    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    except AttributeError as e:
        print(e)
        return 
    if proto == "http:":
        port = 80
    elif proto == "https:":
        import ussl
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)
    prep_time = perf.read_ms()

    #ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)

    ai = usocket.getaddrinfo(host, port)
    ai = ai[0]

    s = usocket.socket(ai[0], ai[1], ai[2])
    s.setblocking(True)
    s.settimeout(5)

    sock_init_time = perf.read_ms() - prep_time
    try:
        s.connect(ai[-1])
        sock_connect_time = perf.read_ms() - sock_init_time
        if proto == "https:":
            s = ussl.wrap_socket(s, server_hostname=host)
        sock_ssl_time = perf.read_ms() - sock_connect_time

        s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
        if not "Host" in headers:
            s.write(b"Host: %s\r\n" % host)
        # Iterate over keys to avoid tuple alloc
        for k in headers:
            s.write(k)
            s.write(b": ")
            s.write(headers[k])
            s.write(b"\r\n")
        if json is not None:
            assert data is None
            import ujson
            data = ujson.dumps(json)
            s.write(b"Content-Type: application/json\r\n")
        if data:
            s.write(b"Content-Length: %d\r\n" % len(data))
        s.write(b"Connection: close\r\n")
        s.write(b"\r\n")
        sock_header_time = perf.read_ms() - sock_ssl_time
        
        if data:
            s.write(data)
        sock_data_time = perf.read_ms() - sock_header_time

        l = s.readline()
        if l is not None:
            l = l.split(None, 2)
            status = int(l[1])
            reason = ""
            if len(l) > 2:
                reason = l[2].rstrip()
        else:
            print("No response")
            status = 0
            reason = ""
        while True:
            l = s.readline()
            if not l or l == b"\r\n":
                break

            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + l)
            elif l.startswith(b"Location:") and not 200 <= status <= 299:
                raise NotImplementedError("Redirects not yet supported")
        sock_response_time = perf.read_ms() - sock_data_time
    except OSError:
        s.close()
        raise

    print("Prep: {:.0f}ms Init: {:.0f}ms Connect: {:.0f}ms SSL: {:.0f}ms "
          "Header: {:.0f}ms Data: {:.0f}ms Response: {:.0f}ms ".format(
              prep_time, sock_init_time, sock_connect_time, sock_ssl_time,
              sock_header_time, sock_data_time, sock_response_time
          ))

    resp = Response(s)
    resp.status_code = status
    resp.reason = reason
    resp.close()
    return resp


def head(url, **kw):
    return request("HEAD", url, **kw)

def get(url, **kw):
    return request("GET", url, **kw)

def post(url, **kw):
    return request("POST", url, **kw)

def put(url, **kw):
    return request("PUT", url, **kw)

def patch(url, **kw):
    return request("PATCH", url, **kw)

def delete(url, **kw):
    return request("DELETE", url, **kw)
