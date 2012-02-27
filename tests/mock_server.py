#!/usr/bin/env python

#-- stdlib imports
import logging
import json
import socket
import sys

#-- third party import
import tornado.httpserver
import tornado.ioloop
import tornado.web


logging.basicConfig(filename='test.log', level=logging.DEBUG)
log = logging.getLogger()


#------------------------------------------------------------- HTTP Handlers --#
class GeneralHandler(tornado.web.RequestHandler):
    def _debug_info(self):
        return json.dumps({'headers': self.request.headers,
                           'body': self.request.body})

    def get(self):
        self.write(self._debug_info())

    def delete(self):
        self.write(self._debug_info())

    def put(self):
        self.write(self._debug_info())

    def post(self):
        self.write(self._debug_info())
# END GeneralHandler


class PingHandler(tornado.web.RequestHandler):
    def get(self):
        """..."""
        log.debug("pong")
        self.write("pong")
# END LookupHandler


#---------------------------------------------------------------- Initiation --#
class Application(tornado.web.Application):
    """Configures the tornado application."""
    def __init__(self):
        handlers = [
            (r"/", GeneralHandler),
            (r"/ping", PingHandler)
        ]

        tornado.web.Application.__init__(self, handlers)
# END Application

if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except ValueError:
        print "Port number must be an int."
        exit(1)
    except IndexError:
        print "Port number are required; eg. 'mp_mock.py 8080'"
        exit(1)
    assert 0 < port <= 65535, \
            "Usage: 'mock_server.py 8080' for a mock on port 8080."

    ssl_options = None
    try:
        if sys.argv[2] == "ssl":
            ssl_options = {"certfile": "../cert/server.crt",
                           "keyfile": "../cert/server.key"}
    except IndexError:
        pass

    if ssl_options:
        server = tornado.httpserver.HTTPServer(Application(),
                                               ssl_options=ssl_options)
    else:
        server = tornado.httpserver.HTTPServer(Application())
    try:
        server.listen(port, "")
    except socket.error, e:
        log.error(e)
        exit(1)

    ioloop = tornado.ioloop.IOLoop.instance()
    log.info("mock server on port %d" % port)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        log.info('Shutting down server')
    finally:
        # Teardown code
        pass
