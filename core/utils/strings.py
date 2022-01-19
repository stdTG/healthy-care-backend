def default_alias_generator(string: str) -> str:
    return no_transform(string)


def to_camel(string: str) -> str:
    c = 0
    result = ''
    for word in string.split('_'):
        c = c + 1
        if c == 1:
            result = result + word
            continue
        result = result + word.capitalize()

    # print("Converted [{A}] to [{B}]".format(A = string, B = result))
    return result


def no_transform(string: str) -> str:
    return string


def dict_with_converted_keys(data: dict, convert=no_transform) -> dict:
    result = {}
    if isinstance(data, dict):
        for key, value in data.items():

            if isinstance(value, dict):
                result[convert(key)] = dict_with_converted_keys(value, convert)
                continue

            result[convert(key)] = value

    elif isinstance(data, list):
        values = []
        for value in data:
            values.append(value)
        return values

    return result


def dict_w_camel_keys(data: dict) -> dict:
    return dict_with_converted_keys(data, to_camel)


def to_pascal(string: str) -> str:
    c = 0
    result = ''
    for word in string.split('_'):
        c = c + 1
        result = result + word.capitalize()

    # print("Converted [{A}] to [{B}]".format(A = string, B = result))
    return result
