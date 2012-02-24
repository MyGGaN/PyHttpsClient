#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#-- stdlib imports
import logging
import unittest

#-- package imports
import base
import https_client.https_client as client

logging.basicConfig(filename='test.log', level=logging.DEBUG)
log = logging.getLogger()


class TestHttpPut(base.ServerTest):
    def test_put_no_body(self):
        req = client.Request(self.server.host, "PUT")
        res = req.send()
        assert res.status == 200, "Failed to put"

    def test_put_with_body(self):
        req = client.Request(self.server.host, "PUT", body="123")
        res = req.send()
        assert res.status == 200, "Failed to put"

if __name__ == '__main__':
    unittest.main()
