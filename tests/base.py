#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#-- stdlib imports
import logging
import subprocess
import unittest
import time
import os

#-- package imports
import https_client.https_client as client

PORT = 8080
client.DEBUG = True

log = logging.getLogger()

if os.path.exists("tests/mock_server.py"):
    mock_path = "tests/mock_server.py"
elif os.path.exists("mock_server.py"):
    mock_path = "mock_server.py"
else:
    assert False, "Couldn't find (tests/)mock_server.py"


class Server():
    def __init__(self, port, ssl=False):
        schema = "https" if ssl else "http"
        self.host = "%s://127.0.0.1:%d" % (schema, port)
        cmd = "python %s %d" % (mock_path, port)
        if ssl:
            cmd += " ssl"
        self.child = subprocess.Popen((cmd).split(), stdout=subprocess.PIPE)
        # Ensure server is up
        time.sleep(.2)
        req = client.Request("%s/ping" % self.host, "GET")
        if ssl:
            req.ssl(cainfo="../cert/ca.crt")
        res = req.send()
        assert res and res.status == 200, "mock_server didn't start."

    def kill(self):
        """Terminates the mock process, GET /admin/shutdown works too."""
        self.child.kill()


class ServerTest(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        pass

    def setUp(self):
        self.server = Server(PORT)

    @classmethod
    def teardown_class(cls):
        pass

    def tearDown(self):
        if hasattr(self, 'server'):
            log.debug("killing server")
            self.server.kill()


class ServerTestSSL(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        pass

    def setUp(self):
        self.server = Server(PORT, True)

    @classmethod
    def teardown_class(cls):
        log.info(1)
        pass

    def tearDown(self):
        log.info(2)
        if hasattr(self, 'server'):
            log.debug("killing server")
            self.server.kill()
