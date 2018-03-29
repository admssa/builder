from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from controller import app
from coralogger import create_logger


if __name__ == "__main__":
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(5000)

    log = create_logger(app)
    log.info("Starting Flask App - KubBuilder")
    log.debug("Additional info about KubBuilder")

    IOLoop.instance().start()
