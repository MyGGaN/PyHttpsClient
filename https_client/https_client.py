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
import logging
import pycurl
import os

log = logging.getLogger()

ACCEPT_HEADER = "*/*"  # Default Accept header
METHOD = {'POST': (pycurl.POST, 1),
          'PUT': (pycurl.PUT, 1),
          'GET': (pycurl.HTTPGET, 1),
          'DELETE': (pycurl.CUSTOMREQUEST, 'DELETE')}
DEBUG = False


class Request(object):
    def __init__(self, url, method, headers=None, body=None):
        body = body or ""
        self.curl = pycurl.Curl()
        if DEBUG:
            self.curl.setopt(pycurl.DEBUGFUNCTION, self._debug)
            self.curl.setopt(pycurl.VERBOSE, 1)
        try:
            self.curl.setopt(*METHOD[method])
        except KeyError:
            log.error("Unsupported method (must be upper case)")
            raise
        self.curl.setopt(pycurl.URL, url)
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

    def progress_callback(self, func):
        """Set up a callback function to track progress.

        def progress(download_t, download_d, upload_t, upload_d):
            print "Total to download", download_t
            print "Total downloaded", download_d
            print "Total to upload", upload_t
            print "Total uploaded", upload_d
        """
        self.curl.setopt(pycurl.PROGRESSFUNCTION, func)

    def post_files(self, file_list):
        """Craft a multipart/formdata HTTP POST.

        file_list -- [("file1_name", "file1_path"), ...]
        """
        self.body = None  # Disable general body to be sent
        f_list = map(lambda f: (f[0], (pycurl.FORM_FILE, f[1])), file_list)
        self.curl.setopt(pycurl.HTTPPOST, f_list)

    def _debug(self, debug_type, debug_msg):
        log.debug("debug(%d): %s" % (debug_type, debug_msg))

    def _set_headers(self):
        if type(self.body) == (str, unicode):
            self.headers['Content-Length'] = len(self.body)
        elif hasattr(self.body, 'fileno'):
            self.headers['Content-Length'] = os.fstat(self.body.fileno())[6]
        if not 'Accept' in self.headers:
            self.headers['Accept'] = ACCEPT_HEADER
        try:
            self.curl.setopt(pycurl.HTTPHEADER,
                             map(lambda key: "%s: %s" % (key, self.headers[key]), self.headers.keys()))
        except TypeError:
            log.error("Failed to set headers")
            raise

    def _set_body(self):
        if hasattr(self.body, 'read') and hasattr(self.body, 'close'):
            self.curl.setopt(pycurl.READFUNCTION, self.body.read)
        else:
            self.curl.setopt(pycurl.READFUNCTION,
                             StringIO.StringIO(self.body).read)

    def send(self):
        self._set_headers()
        if self.body != None:
            self._set_body()
        res = Response()
        self.curl.setopt(pycurl.HEADERFUNCTION, res._header_callback)
        self.curl.setopt(pycurl.WRITEFUNCTION, res._body_callback)
        try:
            self.curl.perform()
        except pycurl.error, msg:
            log.error(*msg)
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
