from typing import Any, Dict, List, Optional
import copy

import flask
import threading
import zmq

from lf_utils.config_utils import instantiate
import lf_utils


class FlaskApp(threading.Thread):
    """Digital Dashboard web app class -- handles data ingestion and visualization"""

    def __init__(
        self,
        data_port: int,
        update_interval: Optional[float] = 1,
    ):
        """Initializes flask app and layout, connects to data socket.

        Parameters
        ----------
        data_port : int
            port to receive data on
        update_interval : Optional[float]
            update interval of dashboard, in seconds (by default 1 second)
        """
        # init thread
        super().__init__()

        # set up data socket
        self.context = zmq.Context()
        self.data_socket = self.context.socket(zmq.PULL)
        lf_utils.retry_utils.retry(
            self.data_socket.bind,
            f"tcp://*:{data_port}",
            handled_exceptions=zmq.error.ZMQError,
        )

        # create flask app
        self.flask_app = flask.Flask(__name__)

        # create flask routes
        self.create_routes()

    def run(self):
        """Runs flask server."""
        self.flask_app.run()

    def shutdown(self):
        """Stops flask server."""
        flask.request.environ.get("werkzeug.server.shutdown")()

    def create_routes(self):
        """Creates flask API routes."""
        self.flask_app.add_url_rule('/', None, self.test)

    def test(self):
        return "Hello world!"
