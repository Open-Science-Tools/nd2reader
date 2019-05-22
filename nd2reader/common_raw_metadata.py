import six
import warnings

from nd2reader.common import get_from_dict_if_exists


def parse_if_not_none(to_check, callback):
    if to_check is not None:
        return callback()
    return None


def parse_dimension_text_line(line):
    if six.b("Dimensions:") in line:
        entries = line.split(six.b("\r\n"))
        for entry in entries:
            if entry.startswith(six.b("Dimensions:")):
                return entry
    return None


def parse_roi_shape(shape):
    if shape == 3:
        return 'rectangle'
    elif shape == 9:
        return 'circle'

    return None


def parse_roi_type(type_no):
    if type_no == 4:
        return 'stimulation'
    elif type_no == 3:
        return 'reference'
    elif type_no == 2:
        return 'background'

    return None


def get_loops_from_data(loop_data):
    loops = [loop_data]
    if six.b('uiPeriodCount') in loop_data and loop_data[six.b('uiPeriodCount')] > 0:
        # special ND experiment
        if six.b('pPeriod') not in loop_data:
            return []

        # take the first dictionary element, it contains all loop data
        loops = loop_data[six.b('pPeriod')][list(loop_data[six.b('pPeriod')].keys())[0]]

        # exclude invalid periods
        if six.b('pPeriodValid') in loop_data:
            loops = [loops[i] for i in range(len(loops)) if loop_data[six.b('pPeriodValid')][i] == 1]

    return loops


def guess_sampling_from_loops(duration, loop):
    """ In some cases, both keys are not saved. Then try to calculate it.
    
    Args:
        duration: the total duration of the loop
        loop: the raw loop data

    Returns:
        float: the guessed sampling interval in milliseconds

    """
    number_of_loops = get_from_dict_if_exists('uiCount', loop)
    number_of_loops = number_of_loops if number_of_loops is not None and number_of_loops > 0 else 1
    interval = duration / number_of_loops
    return interval


def determine_sampling_interval(duration, loop):
    """Determines the loop sampling interval in milliseconds

    Args:
        duration: loop duration in milliseconds
        loop: loop dictionary

    Returns:
        float: the sampling interval in milliseconds

    """
    interval = get_from_dict_if_exists('dPeriod', loop)
    avg_interval = get_from_dict_if_exists('dAvgPeriodDiff', loop)

    if interval is None or interval <= 0:
        interval = avg_interval
    else:
        avg_interval_set = avg_interval is not None and avg_interval > 0

        if round(avg_interval) != round(interval) and avg_interval_set:
            message = ("Reported average frame interval (%.1f ms) doesn't"
                       " match the set interval (%.1f ms). Using the average"
                       " now.")
            warnings.warn(message % (avg_interval, interval), RuntimeWarning)
            interval = avg_interval

    if interval is None or interval <= 0:
        # In some cases, both keys are not saved. Then try to calculate it.
        interval = guess_sampling_from_loops(duration, loop)

    return interval
