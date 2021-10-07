from typing import Any, Dict, Optional

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
        # get machine data from socket
        machine_data = self.data_socket.recv_pyobj()

        # get images to show
        images = [
            self._get_haas_image(machine_data),
            self._get_ecoca_image(machine_data),
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

    def _get_haas_image(self, machine_data: Dict[str, Any]) -> str:
        """Returns path to Haas image to display based on machine data.

        Parameters
        ----------
        machine_data : Dict[str, Any]
            machine data dictionary from LF server

        Returns
        -------
        str
            path to haas image to display
        """
        door_open = f"{'open' if machine_data['haas']['door_open'] else 'closed'}"
        power_on = f"{'on' if machine_data['haas']['input_voltage'] > 0 else 'off'}"
        return self._static_path_for("haas", f"{door_open}_{power_on}")

    def _get_ecoca_image(self, machine_data: Dict[str, Any]) -> str:
        """Returns path to Ecoca image to display based on machine data.

        Parameters
        ----------
        machine_data : Dict[str, Any]
            machine data dictionary from LF server

        Returns
        -------
        str
            path to ecoca image to display
        """
        door_open = f"{'open' if machine_data['ecoca']['door_open'] else 'closed'}"
        power_on = f"{'on' if machine_data['ecoca']['input_voltage'] > 0 else 'off'}"
        return self._static_path_for("ecoca", f"{door_open}_{power_on}")

    @staticmethod
    def _static_path_for(machine_name: str, img_name: str) -> str:
        """Returns static path for image from machine and image name.

        Parameters
        ----------
        machine_name : str
            name of machine to get image for
        img_name : str
            name of image of machine

        Returns
        -------
        str
            path to static image
        """
        return f"static/images/{machine_name}/{img_name}.png"
