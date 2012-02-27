#!/usr/bin/env python
"""Blocking HTTP client with support for client authentication over SSL.

Example:
    url = "https://example.com/test"
    data = json.dumps({"foo": "bar", "spam": "egg"})
    headers = {"Content-Type": "application/json"}

    req = Request(url, "POST", headers=headers, body=data)
    req.ssl(cainfo="ca.crt", verify=True, cert="client.crt", key="client.key")
    res = req.send()
    if res:
        print res.version, res.status, res.reason
        print res.headers
        print res.body
"""

import cStringIO as StringIO
import pycurl

ACCEPT_HEADER = "*/*"  # Default Accept header
#METHOD = ['POST', 'PUT', 'GET', 'HEAD', 'DELETE']
METHOD = {'POST': (pycurl.POST, 1),
          'PUT': (pycurl.PUT, 1),
          'GET': (pycurl.HTTPGET, 1),
          'DELETE': (pycurl.CUSTOMREQUEST, 'DELETE')}
DEBUG = False


def debug(debug_type, debug_msg):
    print "debug(%d): %s" % (debug_type, debug_msg)


def progress(download_t, download_d, upload_t, upload_d):
    print "Total to download", download_t
    print "Total downloaded", download_d
    print "Total to upload", upload_t
    print "Total uploaded", upload_d


class Request(object):
    def __init__(self, url, method, headers=None, body=""):
        self.curl = pycurl.Curl()
        if DEBUG:
            self.curl.setopt(pycurl.DEBUGFUNCTION, debug)
            self.curl.setopt(pycurl.VERBOSE, 1)
        assert method in METHOD, "Unsupported method (must be upper case)"
        self.curl.setopt(*METHOD[method])
        self.curl.setopt(pycurl.URL, url)
        #self.curl.setopt(pycurl.PROGRESSFUNCTION, progress)
        self.headers = headers if headers else dict()
        self.body = body

    def ssl(self, cainfo=None, verify=True, cert=None, key=None):
        """Will let you configure some ssl parameters.

        cainfo - path to the CA cert for the server
        verify - Bool (default True)
        cert   - path to the client cert for client authentication (PEM format)
        """
        if cainfo:
            self.curl.setopt(pycurl.CAINFO, cainfo)

        if verify == False:
            self.curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            self.curl.setopt(pycurl.SSL_VERIFYHOST, 0)
        else:
            self.curl.setopt(pycurl.SSL_VERIFYPEER, 1)
            self.curl.setopt(pycurl.SSL_VERIFYHOST, 2)
        if cert:
            #self.curl.setopt(pycurl.SSLCERTTYPE, "DER")
            self.curl.setopt(pycurl.SSLCERT, cert)
        if key:
            self.curl.setopt(pycurl.SSLKEY, key)

    def _set_headers(self):
        self.headers['Content-Length'] = len(self.body)
        if not 'Accept' in self.headers:
            self.headers['Accept'] = ACCEPT_HEADER
        #self.headers['Expect'] = "100-continue"
        headers = map(lambda key: "%s: %s" % (key, self.headers[key]),
                      self.headers.keys())
        self.curl.setopt(pycurl.HTTPHEADER, headers)

    def _set_body(self):
        fp = StringIO.StringIO(self.body)
        self.curl.setopt(pycurl.READFUNCTION, fp.read)

    def send(self):
        self._set_headers()
        #self.curl.setopt(pycurl.NOBODY, 0)
        self._set_body()
        res = Response()
        self.curl.setopt(pycurl.HEADERFUNCTION, res._header_callback)
        self.curl.setopt(pycurl.WRITEFUNCTION, res._body_callback)
        try:
            self.curl.perform()
        except pycurl.error, msg:
            debug(*msg)
            return None
        res.status = self.curl.getinfo(pycurl.HTTP_CODE)
        self.curl.close()
        return res


class Response(object):
    """HTTP response class."""
    def __init__(self):
        self._chunks = list()
        self.version = None
        self.status = None
        self.reason = None
        self.headers = dict()

    def _body_callback(self, chunk):
        #print "_bc: %s" % chunk
        self._chunks.append(chunk)

    def _header_callback(self, header):
        #print "_hc: %s" % header
        header = header.rstrip()  # Remove trailing \r\n
        if not header:
            return
        if header.startswith("HTTP/1."):
            self.version, status, self.reason = header.split(None, 2)
            #self.status = int(status)  # Already set
            return
        header, value = header.split(': ', 1)
        self.headers[header] = value

    body = property(fget=lambda self: ''.join(self._chunks))
