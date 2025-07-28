import pytest
from project import is_within, are_equal, determine_square_grid_in_list, create_regex, get_full_directory, get_save_slot_dir

def test_is_within():
    assert is_within(height=20, width=20, x=2, y=0) == True

def test_get_save_slot_dir():
    assert get_save_slot_dir(number=1) == "saves/save_slot_1"

def test_get_full_directory():
    assert get_full_directory(slot_number=1, data_name="player") == "saves/save_slot_1/save_1_player.txt"
    assert get_full_directory(slot_number=1, data_name="current_map") == "saves/save_slot_1/save_1_current_map.txt"
