from datetime import date


def generate_index(target_date: date) -> int:
    return int(f"{target_date.year}{target_date.month:02d}")


def generate_index_from_int(month: int, year: int) -> int:
    return int(f"{year}{month:02d}")


def generate_index_from_str(date: str):
    split_index = date.split("-")
    index = "".join([split_index[0], split_index[1]])

    return int(index)
