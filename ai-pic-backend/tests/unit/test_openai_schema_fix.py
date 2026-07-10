"""test OpenAI provider   JSON schema additionalProperties repair"""

from app.services.providers.openai_provider import (
    _add_additional_properties_false,
    _is_openai_strict_schema,
)


def test_add_additional_properties_to_simple_object():
    """test for Jian Dan object Tian Jia additionalProperties: false"""
    schema = {
        "type": "object",
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
    }

    result = _add_additional_properties_false(schema)

    assert result["additionalProperties"] is False
    assert "properties" in result
    assert result["properties"]["name"] == {"type": "string"}


def test_add_additional_properties_to_nested_objects():
    """test for Qian Tao object Di Gui Tian Jia additionalProperties: false"""
    schema = {
        "type": "object",
        "properties": {
            "user": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "address": {
                        "type": "object",
                        "properties": {"city": {"type": "string"}},
                    },
                },
            }
        },
    }

    result = _add_additional_properties_false(schema)

    # Ding Ceng object
    assert result["additionalProperties"] is False

    # Qian Tao user object
    user_schema = result["properties"]["user"]
    assert user_schema["additionalProperties"] is False

    # Geng Shen Ceng address object
    address_schema = user_schema["properties"]["address"]
    assert address_schema["additionalProperties"] is False


def test_add_additional_properties_to_array_items():
    """test for Shu Zuitemsin object Tian Jia additionalProperties: false"""
    schema = {
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {"type": "object", "properties": {"id": {"type": "string"}}},
            }
        },
    }

    result = _add_additional_properties_false(schema)

    # Ding Ceng object
    assert result["additionalProperties"] is False

    # Shu Zuitemsin object
    item_schema = result["properties"]["items"]["items"]
    assert item_schema["additionalProperties"] is False


def test_add_additional_properties_with_defs():
    """test handle $defs (definitions) in object"""
    schema = {
        "type": "object",
        "properties": {"data": {"$ref": "#/$defs/DataObject"}},
        "$defs": {
            "DataObject": {
                "type": "object",
                "properties": {"value": {"type": "string"}},
            }
        },
    }

    result = _add_additional_properties_false(schema)

    # Ding Ceng object
    assert result["additionalProperties"] is False

    # $defs in object
    data_object = result["$defs"]["DataObject"]
    assert data_object["additionalProperties"] is False


def test_add_additional_properties_with_anyof():
    """test handle anyOf in object"""
    schema = {
        "type": "object",
        "properties": {
            "value": {
                "anyOf": [
                    {"type": "string"},
                    {"type": "object", "properties": {"complex": {"type": "boolean"}}},
                ]
            }
        },
    }

    result = _add_additional_properties_false(schema)

    # Ding Ceng object
    assert result["additionalProperties"] is False

    # anyOf in object
    any_of_items = result["properties"]["value"]["anyOf"]
    assert any_of_items[0] == {"type": "string"}  # Fei object type Bu Bian
    assert (
        any_of_items[1]["additionalProperties"] is False
    )  # object type Tian Jia additionalProperties


def test_preserves_existing_additional_properties():
    """test Bao Liu already exists additionalProperties set"""
    schema = {
        "type": "object",
        "additionalProperties": True,  # already exists，Dan Hui be Fu Gai for False
        "properties": {"name": {"type": "string"}},
    }

    result = _add_additional_properties_false(schema)

    # OpenAI Yao Qiu Bi Xu for False，Suo Yi Fu Gai Yuan Zhi
    assert result["additionalProperties"] is False


def test_does_not_modify_non_objects():
    """test not Xiu Gai Fei object type"""
    schema = {"type": "string"}

    result = _add_additional_properties_false(schema)

    assert result == {"type": "string"}
    assert "additionalProperties" not in result


def test_openai_strict_schema_rejects_generic_object_items():
    schema = {
        "type": "object",
        "properties": {
            "dialogues": {"type": "array", "items": {"type": "object"}},
        },
    }
    fixed = _add_additional_properties_false(schema)
    assert _is_openai_strict_schema(fixed) is False


def test_openai_strict_schema_accepts_typed_object_items():
    schema = {
        "type": "object",
        "properties": {
            "dialogues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {"content": {"type": "string"}},
                },
            },
        },
    }
    fixed = _add_additional_properties_false(schema)
    assert _is_openai_strict_schema(fixed) is True
