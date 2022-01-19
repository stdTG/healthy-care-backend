SchemaAttributes = {
    "Email": {
        "Name": "email",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": False,
        "Mutable": True,
        "Required": True,
        "StringAttributeConstraints": {
            "MinLength": "0",
            "MaxLength": "2048"
        }
    },
    "PhoneNumber": {
        "Name": "phone_number",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": False,
        "Mutable": True,
        "Required": True,
        "StringAttributeConstraints": {
            "MinLength": "0",
            "MaxLength": "2048"
        }
    },
    "Custom_ObjectId": {
        "Name": "objectid",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": False,
        "Mutable": True,
        "Required": False,
        "StringAttributeConstraints": {
            "MinLength": "0",
            "MaxLength": "255"
        }
    },
    "Custom_OrgUnitId": {
        "Name": "orgunitid",
        "AttributeDataType": "String",
        "DeveloperOnlyAttribute": False,
        "Mutable": True,
        "Required": False,
        "StringAttributeConstraints": {
            "MinLength": "0",
            "MaxLength": "255"
        }
    }
}
