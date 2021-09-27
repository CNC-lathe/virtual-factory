from virtual_factory import FlaskApp

def test_integration(update_interval: float):
    """Runs flask app

    Parameters
    ----------
    update_interval : float
        update interval for MockLFServer
    """
    # init flask app
    flask_app = FlaskApp(49160)

    # start flask app
    flask_app.start()

    # wait for user to exit
    input("Press any key to go to next test")


if __name__ == "__main__":
    update_interval = 1.0

    test_integration(update_interval)
