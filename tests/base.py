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
client.DEBUG = False

log = logging.getLogger()

assert os.path.exists("mock_server.py"), \
        "You have to be in tests/ to find the mock_server.py"


class Server():
    def __init__(self, port):
        self.host = "http://127.0.0.1:%d" % port
        self.child = subprocess.Popen(
                ("python mock_server.py %d" % port).split(),
                stdout=subprocess.PIPE)
        # Ensure server is up
        time.sleep(.2)
        req = client.Request("%s/ping" % self.host, "GET")
        res = req.send()
        assert res and res.status == 200, "mock server didn't start."

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
