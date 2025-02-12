import pytest
from src.lcseq.core.building_block import BuildingBlock


class TestBuildingBlock:
    """Test suite for BuildingBlock class."""

    def test_building_block_initialization(self):
        """Test basic initialization of BuildingBlock."""
        identifier = "test_block"
        properties = {"key": "value"}
        block = BuildingBlock(identifier=identifier, properties=properties)

        assert isinstance(block, BuildingBlock)
        assert block.identifier == identifier
        assert block.properties == properties

    def test_building_block_empty_initialization(self):
        """Test initialization with empty properties."""
        identifier = "test_block"
        block = BuildingBlock(identifier=identifier, properties={})

        assert isinstance(block, BuildingBlock)
        assert block.identifier == identifier
        assert block.properties == {}

    def test_building_block_properties_access(self):
        """Test property access."""
        identifier = "test_block"
        initial_properties = {"test_key": "test_value"}
        block = BuildingBlock(identifier=identifier, properties=initial_properties)

        assert block.properties["test_key"] == "test_value"

        # Test accessing non-existent property
        with pytest.raises(KeyError):
            _ = block.properties["non_existent"]

    def test_building_block_property_modification(self):
        """Test property modification."""
        identifier = "test_block"
        initial_properties = {"test_key": "initial_value"}
        block = BuildingBlock(identifier=identifier, properties=initial_properties)

        # Modify existing property
        block.properties["test_key"] = "new_value"
        assert block.properties["test_key"] == "new_value"

        # Add new property
        block.properties["new_key"] = "value"
        assert block.properties["new_key"] == "value"

    def test_building_block_property_types(self):
        """Test different property value types."""
        identifier = "test_block"
        test_values = {
            "string": "test",
            "integer": 42,
            "float": 3.14,
            "list": [1, 2, 3],
            "dict": {"key": "value"},
            "none": None,
        }

        block = BuildingBlock(identifier=identifier, properties=test_values)

        for key, value in test_values.items():
            assert block.properties[key] == value

    def test_building_block_invalid_initialization(self):
        """Test initialization with invalid parameters."""
        with pytest.raises(ValueError):
            BuildingBlock(identifier="", properties={})

        with pytest.raises(TypeError):
            BuildingBlock(identifier=None, properties={})

        with pytest.raises(TypeError):
            BuildingBlock(identifier="test", properties=None)
