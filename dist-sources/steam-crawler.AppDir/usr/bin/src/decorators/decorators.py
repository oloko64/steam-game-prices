from time import time


def timeit(func):
    def wrap_func(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        print()
        print(f'Program took {round((end - start), 3)}s to run')
        return result
    return wrap_func


@timeit
def print_welcome():
    print('Welcome to datagy!')
