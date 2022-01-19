data = {
    "sample_field_1": "sample_field_1_value",
    "sample_field_2": "sample_field_2_value",
    "sample_field_3": {
        "sub_field_3_1": True,
        "sub_filed_3_2": True,
        "sub_field_3_3": 343
    },
    "sample_field_array": [4, 3, 1, 45, 13],
    "sample_field_5": {
        "sub_field_5_1": "simple",
        "sub_field_5_2": {
            "sub_sub_field_5_2_1": "value 1",
            "sub_sub_field_5_2_2": ["A", "B", "C"],
            "sub_sub_field_5_2_3": "value 3",
        }
    }
}

camelized_keys = {
    'sampleField1': 'sample_field_1_value',
    'sampleField2': 'sample_field_2_value',
    'sampleField3': {
        'subField31': True,
        'subFiled32': True,
        'subField33': 343
    },
    'sampleFieldArray': [4, 3, 1, 45, 13],
    'sampleField5': {
        'subField51': 'simple',
        'subField52': {
            'subSubField521': 'value 1',
            'subSubField522': ['A', 'B', 'C'],
            'subSubField523': 'value 3'
        }
    }
}
