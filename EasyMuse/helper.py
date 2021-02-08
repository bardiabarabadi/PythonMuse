import platform


def is_data_valid(data, timestamps):
    if timestamps == 0.0:
        return False
    if all(data == 0.0):
        return False
    return True


def PPG_error(Exceptions):
    pass
