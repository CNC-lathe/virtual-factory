from typing import List, Optional

import flask
import threading
import zmq

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
        self.flask_app = flask.Flask(
            __name__, static_url_path="", template_folder="./templates/"
        )

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
        self.flask_app.add_url_rule('/', None, self.virtual_factory_page)
        self.flask_app.add_url_rule('/_machines', None, self.virtual_factory_machines)
        self.flask_app.add_url_rule("/static/<path:path>", None, self.send_static)

    def virtual_factory_page(self) -> str:
        """Renders and returns virtual factory page.

        Returns
        -------
        str
            HTML string of rendered virtual factory page
        """
        return flask.render_template(
            "virtual_factory.html",
        )

    def virtual_factory_machines(self) -> str:
        """Renders and returns virtual factory machines.

        Returns
        -------
        str
            HTML string of rendered virtual factory machine images
        """
        print("IN VIRTUAL FACTORY MACHINES")
        # get machine data from socket
        machine_data = self.data_socket.recv_pyobj()

        # get images to show
        images = [
            "static/images/haas/base.png",
            "static/images/ecoca/base.png",
        ]

        return flask.render_template(
            "virtual_machines.html",
            machine_images=images,
        )

    def send_static(self, path: str) -> flask.Response:
        """Sends static file.

        Returns
        -------
        flask.Response
            static file requested
        """
        return flask.send_from_directory("static", path)
