import pytest
from project import (
    is_within,
    are_equal,
    determine_square_grid_in_list,
    create_regex,
    get_full_directory,
    get_save_slot_dir,
    sq_increment_range)


def test_is_within():
    assert is_within(height=20, width=20, x=2, y=0) == True

def test_get_save_slot_dir():
    assert get_save_slot_dir(number=1) == "saves/save_slot_1"

def test_get_full_directory():
    assert get_full_directory(slot_number=1, data_name="player") == "saves/save_slot_1/save_1_player.txt"
    assert get_full_directory(slot_number=1, data_name="current_map") == "saves/save_slot_1/save_1_current_map.txt"

def test_sq_increment_range():
    assert sq_increment_range(1) == range(-1,2)
    assert sq_increment_range(2) == range(-2,3)

    with pytest.raises(ValueError) as excinfo:
        sq_increment_range(0)
    assert str(excinfo.value) == "torch_level_in must be an int x, x >= 1"
