#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#-- stdlib imports
import logging
import unittest
import json

#-- package imports
import base
import https_client.https_client as client

logging.basicConfig(filename='test.log', level=logging.DEBUG)
log = logging.getLogger()


class TestHttpGet(base.ServerTest):
    def test_get(self):
        headers = {'Foo': "bar"}
        req = client.Request(self.server.host, "GET", headers=headers)
        res = req.send()
        assert res.status == 200, "Failed to get"

        # Assert server received correct request
        server_request = json.loads(res.body)
        body = server_request['body']
        headers = server_request['headers']
        assert len(body) == 0, "Request contained body"
        assert headers['Content-Length'] == "0", "Content-Length was not 0"
        try:
            assert headers['Foo'] == "bar", "Foo header have wrong value"
        except KeyError:
            assert False, "Foo header missing"

if __name__ == '__main__':
    unittest.main()
