def str_to_bool(value: str):
    if value.lower() in ['true', '1']:
        return True
    elif value.lower() in ['false', '0']:
        return False
    else:
        raise ValueError(f'Cannot parse "{value}" into bool')