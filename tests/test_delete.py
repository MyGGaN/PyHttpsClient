#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#-- stdlib imports
import logging
import nose
import unittest

#-- package imports
import base
import https_client.https_client as client

logging.basicConfig(filename='test.log', level=logging.DEBUG)
log = logging.getLogger()


class TestHttpPost(base.ServerTest):
    @nose.tools.timed(1)
    def test_post_no_body(self):
        req = client.Request(self.server.host, "DELETE")
        res = req.send()
        assert res.status == 200, "Failed to post"

if __name__ == '__main__':
    unittest.main()
