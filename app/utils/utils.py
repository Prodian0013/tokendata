from functools import wraps
from time import sleep
import requests
from requests import Response


class APIFailure(Exception):
    pass

def retry(count=5, time_to_sleep_between_retries=20):
    """
    A function wrapper that can be used to auto retry the wrapped function if
    it fails.  To use this function

    @retry(count=10)
    def somefunction():
        pass

    :param count: The number of retries it will perform.
    :param time_to_sleep_between_retries: The time to sleep between retries.
    :return:
    """
    def decorator(func):
        @wraps(func)
        def result(*args, **kwargs):
            for i in range(count):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if (i + 1) == count:
                        raise
                    print(str(e))
                    print("Sleeping {} seconds".format(time_to_sleep_between_retries))
                    sleep(time_to_sleep_between_retries)
        return result
    return decorator

def generate_block_ranges(starting_block, ending_block, range_size):
    if range_size == 0:
        return []

    start = int(starting_block)
    end_block_number = int(ending_block)
    while start + range_size <= end_block_number:
        end = start + range_size
        yield start, end
        start = end + 1
    yield start, end_block_number

@retry(count=10, time_to_sleep_between_retries=2)
def get_data(uri):
    response = requests.get(uri) # type: Response
    if response.status_code == 200:
        return response.json()
    else:
        raise APIFailure(uri + ' FAILED!\n' + str(response.status_code))