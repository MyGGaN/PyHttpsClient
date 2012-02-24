#!/usr/bin/env python

#-- stdlib imports
import logging
import sys

#-- third party import
import tornado.httpserver
import tornado.ioloop
import tornado.web


logging.basicConfig(filename='test.log', level=logging.DEBUG)
log = logging.getLogger()


#------------------------------------------------------------- HTTP Handlers --#
class GeneralHandler(tornado.web.RequestHandler):
    def get(self):
        pass

    def delete(self):
        pass

    def put(self):
        pass

    def post(self):
        """..."""
        log.error("aaa")
        log.debug("headers: %s" % self.request.headers)
        log.debug("body: %s" % self.request.body)
        self.write("post")
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
        print "Port number are required; eg. 'mp_mock.py 80'"
        exit(1)
    assert 0 < port <= 65535, "Usage: 'mock_server.py 80' for a mock on port 80."

    server = tornado.httpserver.HTTPServer(Application())
    server.listen(port, "")

    ioloop = tornado.ioloop.IOLoop.instance()
    log.info("mock server on port %d" % port)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        log.info('Shutting down server')
    finally:
        # Teardown code
        pass
