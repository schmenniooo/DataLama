"""Client input validation module"""

def validate_data_to_analyse(data_sets: list[str]) -> str:
    if len(data_sets) == 0:
        return "Data cannot be empty"

    for data_set in data_sets:
        if len(data_set) == 0:
            return "Single data sets cannot be emtpy"

    return ""

