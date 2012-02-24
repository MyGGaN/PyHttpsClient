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


class TestHttpDelete(base.ServerTest):
    def test_delete(self):
        req = client.Request(self.server.host, "DELETE")
        res = req.send()
        assert res.status == 200, "Failed to post"

if __name__ == '__main__':
    unittest.main()
