from core.utils.strings import dict_with_converted_keys, to_camel
from core.utils.unit_tests.sample_data import data

converted = dict_with_converted_keys(data, to_camel)
print(converted)
