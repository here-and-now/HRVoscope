import re
from pathlib import Path
import platform

from PySide6.QtGui import QColor

BLUE = QColor(135, 206, 250)
WHITE = QColor(255, 255, 255)
GREEN = QColor(0, 255, 0)
YELLOW = QColor(255, 255, 0)
RED = QColor(255, 0, 0)


def get_sensor_address(sensor):
    """Return MAC (Windows, Linux) or UUID (macOS)."""
    system = platform.system()
    if system in ["Linux", "Windows"]:
        return sensor.address().toString()
    elif system == "Darwin":
        return sensor.deviceUuid().toString().strip("{}")

def get_seconds_from_button_text(button):
    """Return seconds from button text."""
    text = button.text()
    period_number = int(text[:-1])
    period_unit = text[-1]

    seconds = {k: v for k, v in {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}.items() if k == period_unit}[period_unit] * period_number

    return seconds
def get_sensor_remote_address(sensor):
    """Return MAC (Windows, Linux) or UUID (macOS)."""
    system = platform.system()
    if system in ["Linux", "Windows"]:
        return sensor.remoteAddress().toString()
    elif system == "Darwin":
        return sensor.remoteDeviceUuid().toString().strip("{}")


def valid_address(address):
    """Make sure that MAC (Windows, Linux) or UUID (macOS) is valid."""
    valid = False
    system = platform.system()

    if system in ["Linux", "Windows"]:
        regex = re.compile("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$")
        valid = regex.match(address.lower())
    elif system == "Darwin":
        regex = re.compile(
            "[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[0-9a-f]{4}-[0-9a-f]{12}$"  # polar uuid not necessarily RFC4122 compliant
        )
        valid = regex.match(address.lower())

    return valid


def valid_path(path):
    """Make sure that path is valid by OS standards and that a file doesn't
    exist on that path already. No builtin solution for this atm."""
    valid = False
    test_path = Path(path)

    try:
        test_path.touch(exist_ok=False)  # create file
        test_path.unlink()  # remove file (only called if file doesn't exist)
        valid = True
    except OSError:  # path exists or is invalid
        pass

    return valid


def find_indices_to_average(seconds, mean_window):
    """Identify which elements need to be averaged.

    Find the indices of those seconds that fall within the most recent
    `mean_window` seconds.

    Parameters
    ----------
    seconds : ndarray of float
        Vector of seconds corresponding to sampling moments. Can be sampled
        non-uniformly. The right-most element is the most recent.
    mean_window : float
        Average window in seconds.

    Returns
    -------
    mean_indices : bool
        Boolean indices indicating which elements in `seconds` need to be
        averaged.
    """
    mean_indices = seconds >= -mean_window
    if not sum(mean_indices):
        # make sure that at least one element gets selected
        mean_indices[-1] = True
    return mean_indices

@staticmethod
def convert_array_to_signed_int(data, offset, length):
    return int.from_bytes(
        bytearray(data[offset: offset + length]), byteorder="little", signed=True,
    )

@staticmethod
def convert_to_unsigned_long(data, offset, length):
    return int.from_bytes(
        bytearray(data[offset: offset + length]), byteorder="little", signed=False,
    )

