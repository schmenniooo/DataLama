"""Client input validation module"""

def validate_data_sets(data_sets: list[str]) -> bool:
    if len(data_sets) == 0:
        return False

    for data_set in data_sets:
        if len(data_set) == 0:
            return False

    return True

