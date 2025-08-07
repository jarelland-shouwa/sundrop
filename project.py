'''
# TODO The program should have sufficient comments,
# which includes your name, class, date, overall
# description of what the program does, as well
# as the description of the functions.
'''

from random import randint
import os
import re

player: dict[str, str | int] = {}
current_map: list[list[str]] = [] # originally named game_map
fog: list[list[str]] = []

MAP_WIDTH: int = 0
MAP_HEIGHT: int = 0

TURNS_PER_DAY: int = 20
WIN_GP: int = 500

minerals: list[str] = ['copper', 'silver', 'gold']
mineral_names: dict[str, str] = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_prices: list[int] = [50, 150]

prices: dict[str, tuple[int, int]] = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

# NEW
pieces_per_node: dict[str, tuple[int, int]] = {}
pieces_per_node['copper'] = (1, 5)
pieces_per_node['silver'] = (1, 3)
pieces_per_node['gold'] = (1, 2)

# Dynamic
current_prices: dict[str, int] = {}

current_save_slot: int = 1 # Needs to be globalised
SAVE_SLOT_QUANTITY: int = 5

WASD_TO_DIRECTION_AND_MOVE_VALUE: dict[str, dict[str, str | int]]= {
    "w": {"direction": "y", "move_value": -1},
    "a": {"direction": "x", "move_value": -1},
    "s": {"direction": "y", "move_value": 1},
    "d": {"direction": "x", "move_value": 1}}

SAVE_SLOT_DIRECTORY_PREFIX: str = "saves/save_slot"
# E.g. saves/save_slot_1 (to be done by get_save_slot_dir)

game_state: str = "main" # can be "main", "exit", "town", "mine"
FILES_TO_SAVE: tuple[str, str, str] = ("fog", "current_map", "player")

TOWN_POSITION: tuple[int, int] = (0, 0)
TORCH_LEVEL_LIMIT: int = 3
BACKPACK_UPGRADE_CONSTANT: int = 2 # Used to find 1. cost of backpack upgrade
# and 2. capacity increase
TORCH_UPGRADE_MULTIPLIER: int = 25

high_score_records: dict = {}
TOP_PLAYERS_QUANTITY: int = 5
ARCHIVE_FILE_NAME: str = "past_players.txt"

FOG_CHAR = "?"
NON_FOG_CHAR = " "
PLAYER_CHAR = "M"
# ------------------------- GENERAL Functions -------------------------


def validate_input(message: str, regex: str, is_single: bool) -> str:
    """Uses a regular expression to validate input
    (best for single char input). is_single specifies if
    the input is a single character (e.g. for menu selections)
    If is_single == False, input will be categorised
    as the following examples:
    Note: "bob, gates CEO" will be INVALID for name var (cannot contain ",")
    ```
    VALID = ["bob", "bob gates", "bob  gates CEO"]
    INVALID = ["\n", "\t", " ", " bob ", "\tbob\t", "bob\tgates", ""]```
    """

    while True:
        user_input: str = input(message)
        if is_single and re.match(regex, user_input.lower()):
            return user_input.lower()

        has_tabs: bool =  user_input.find("\t") != -1
        has_invalid_spaces: bool = user_input.startswith(" ") or user_input.endswith(" ")
        has_new_lines: bool = user_input.find("\n") != -1
        has_invalid_whitespaces: bool = has_invalid_spaces or has_new_lines or has_tabs
        duplicate_name: bool = user_input in high_score_records

        if re.match(regex, user_input) and not has_invalid_whitespaces and not duplicate_name:
            return user_input

        if user_input == "":
            print("Please enter a valid input instead of nothing.")
        elif "," in user_input:
            print("Commas (,) are not allowed. Please enter input without it.")
        elif has_invalid_whitespaces:
            print("Please enter a valid input that does not contain unnecessary/invalid whitespace.")
        elif duplicate_name:
            print("That name has already been taken. Please enter another name.")
        else:
            print(f"{user_input} is invalid. Please enter a valid input.")


def save_list_to_txt(filename: str, input_list: list) -> None:
    '''Saves a list into a text file.'''

    with open(filename, "w", encoding="utf-8") as save_file_map:
        text_to_write: str = ""
        for row in input_list:
            for element in row:
                text_to_write += element
            text_to_write += "\n"
        text_to_write = text_to_write[:len(text_to_write)-1] # remove extra \n
        save_file_map.write(text_to_write)


def is_within(height: int, width: int, x: int, y: int) -> bool:
    '''Checks if a position is within the boundaries of a 2D list.'''
    return 0 <= y <= (height-1) and 0 <= x <= (width-1)


def are_equal(y1: int, y2: int, x1: int, x2: int) -> bool:
    '''Checks if two positions are equal.'''
    return x1 == x2 and y1 == y2

# ✅✅✅
def get_pos_in_square(x: int, y: int,
                                  list_height: int,
                                  list_width: int,
                                  torch_level: int) -> list[dict[str, int]]:
    """Returns positions that are within a square of side 3
    (adjusted by torch_level) as the (x,y) the centre.
    I.e. positions that are within a Manhattan Distance of 2 units,

    Returns
    -------
    list[dict[str, int]]
        valid_positions; E.g. [pos_dict_1, pos_dict_2, pos_dict_3, ...]
    """

    valid_positions: list[dict[str, int]] = []
    # invalid_positions: list[dict[str, int]] = []
    sq_range: range = sq_increment_range(torch_level)

    for i in sq_range:
        row_n: int = y + i
        for j in sq_range:
            col_n: int = x + j

            if is_within(height=list_height, width=list_width, x=col_n, y=row_n):
                valid_positions.append({"x": col_n, "y": row_n})
            # else:
            #     invalid_positions.append({"x": col_n, "y": row_n})
    return valid_positions


def create_regex(valid_char: str) -> str:
    '''Creates a raw expression for regex that only accepts certain single characters.'''
    return rf"^[{valid_char}]$"


def get_file_name(slot_number: int, data_name: str) -> str:
    '''Returns the file name for a txt file to be saved in a save slot.'''
    return f"save_{slot_number}_{data_name}.txt"


def get_save_slot_dir(number: int) -> str:
    '''Returns save slot directory name based on slot number.'''
    return f"{SAVE_SLOT_DIRECTORY_PREFIX}_{number}"


def get_full_directory(slot_number: int, data_name: str) -> str:
    '''Returns the full directory path for a txt file to be saved in a save slot.'''
    directory_name: str = get_save_slot_dir(number=slot_number)
    file_name: str = get_file_name(slot_number=slot_number, data_name=data_name)
    return f"{directory_name}/{file_name}"


def sq_increment_range(torch_level_in: int) -> range:
    """Helps in finding the valid positions
    from centre position in a square.
    E.g. for torch_level_in = 1, i.e. side length = 3 units;
    from centre (a, b),
    with the returned range(-1, 2),
    we can find all of the valid positions:
    ```
    for i in range(-1, 2):
        for j in range(-1, 2):
            valid_position = (a+i, b+j)
    ```
    Parameters
    ----------
    torch_level_in : int
        Valid values = 1 to TORCH_LEVEL_LIMIT, all inclusive

    Returns
    -------
    range
        increment from centre position

    Raises
    ------
    ValueError
        Raised if side_length value is invalid.
    """

    if not(isinstance(torch_level_in, int) and 1 <= torch_level_in <= TORCH_LEVEL_LIMIT):
        raise ValueError("torch_level_in must be an int x, 1 <= x <= TORCH_LEVEL_LIMIT")
    return range(0-torch_level_in, 1+torch_level_in)


# ------------------------- Initialise-, Load-, Save-related Functions -------------------------


def find_written_slots(mode: str) -> list[int]:
    '''
    Checks all of the save slot folders to see if they are empty or not.
    Takes in a mode for different print messages.
    Returns a list of save slots that has data already written to it.

    Mode can be "save", "load".
    '''

    if mode not in ["save", "load"]:
        raise ValueError(f"{mode} is invalid. Valid: {["save", "load"]}. Please check again.")

    save_slot_listing_text: str = ""
    written_colour, empty_colour = 91, 92
    if mode == "save":
        save_slot_listing_text: str = "Select a save slot to save to.\n"
    elif mode == "load":
        save_slot_listing_text: str = "Select a save slot to load from.\n"
        written_colour, empty_colour = 92, 91

    written_slots: list[int] = []
    for i in range(1, SAVE_SLOT_QUANTITY+1):
        try:
            files_in_dir: list[str] = os.listdir(get_save_slot_dir(number=i))
        except FileNotFoundError:
            assert False, f"\033[91m{f"Slot {i}: EMPTY ; FileNotFoundError; Please check that this folder has been created."}\033[00m"
        else:
            files_needed: set = {get_file_name(i, name) for name in FILES_TO_SAVE}

            # files_in_dir == [get_file_name(i, name) for name in FILES_TO_SAVE]
            if files_needed.issubset(set(files_in_dir)):
                written_slots.append(i)
                save_slot_listing_text += f"\033[{written_colour}m{f"Slot {i}: HAS BEEN WRITTEN TO\n"}\033[00m"
            elif 0 < len(files_in_dir) < len(FILES_TO_SAVE) and mode == "load":
                save_slot_listing_text += f"\033[{empty_colour}m{f"Slot {i}: Incorrect number of files present. Check files again.\n"}\033[00m"
            elif len(files_in_dir) == len(FILES_TO_SAVE) and mode == "load":
                save_slot_listing_text += f"\033[{empty_colour}m{f"Slot {i}: Check files again. Could be file name or type of file issue.\n"}\033[00m"
            else:
                save_slot_listing_text += f"\033[{empty_colour}m{f"Slot {i}: EMPTY ; No files in save folder\n"}\033[00m"

    # Lists whether a save slot is empty or has data already written to it.
    print(save_slot_listing_text)
    return written_slots


def choose_new_save_slot() -> int:
    """Allows choosing of save slot to begin a NEW game.

    Returns
    -------
    int
        save slot choice
    """

    written_slots: list[int] = find_written_slots(mode="save")

    # Creating regex for input validation based on number of save slots.
    regex: str = "".join([str(i) for i in list(range(1,SAVE_SLOT_QUANTITY+1))])
    regex = create_regex(valid_char=regex)

    # Asking user for desired save slot choice
    while True:
        save_slot_choice: int = int(validate_input("Your choice? ", regex, True))
        if save_slot_choice in written_slots:
            confirmation_choice: str = validate_input(f"Are you sure? This will overwrite save "
                                                 f"slot {save_slot_choice}. "
                                                 "Your choice (y/n)? ", r"^[yn]$", True)
            if confirmation_choice == "n":
                print(f"You chose not to overwrite save slot {save_slot_choice}")
                continue
        break

    return save_slot_choice


# Template
def load_map(filename: str, map_struct: list) -> None:
    '''
    Loads a map structure (a nested list) from a file.
    Updates MAP_WIDTH and MAP_HEIGHT.
    Saves data to map_struct.'''
    global MAP_WIDTH
    global MAP_HEIGHT

    with open(filename, 'r', encoding="utf-8") as map_file:
        map_struct.clear()

        lines: list[str] = map_file.read().split("\n")
        for line in lines:
            row: list[str] = list(line)
            map_struct.append(row)

        MAP_WIDTH = len(map_struct[0])
        MAP_HEIGHT = len(map_struct)


# Template ✅✅✅
def clear_fog(fog_in: list[list[str]], player_in: dict[str, str | int]) -> None:
    """This function clears the fog of war at the 3x3
    square around the player. (adjusted by torch level)

    Parameters
    ----------
    fog_in : list[list[str]]
        input for GLOBAL fog (originally named fog)
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    positions_to_update: list[dict[str, int]] = get_pos_in_square(x=player_in["x"],
                                                            y=player_in["y"],
                                                            list_height=MAP_HEIGHT,
                                                            list_width=MAP_WIDTH,
                                                            torch_level=player_in["torch_level"])

    for position in positions_to_update:
        y = position["y"]
        x = position["x"]
        fog_in[y][x] = NON_FOG_CHAR


# Template ✅✅✅
def initialize_game(current_map_in: list[list[str]],
                    fog_in: list[list[str]], player_in: dict[str, str | int]) -> None:
    """Initiliases current_map, fog and player information.

    Parameters
    ----------
    current_map_in : list[list[str]]
        input for GLOBAL game map (originally named game_map)
    fog_in : list[list[str]]
        input for GLOBAL fog (originally named fog)
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    global current_save_slot

    current_save_slot = choose_new_save_slot()
    name: str = validate_input("Greetings, miner! What is your name? ", r"^[^,\n\t]+$", False)

    # initialise current map
    current_map_in.clear()
    try:
        load_map(filename="level1.txt", map_struct=current_map_in)
    except FileNotFoundError:
        print("FileNotFoundError; Please check that the level map exists again.")

    # initialise fog
    fog_in.clear()
    for _ in range(MAP_HEIGHT):
        row: list[str] = [FOG_CHAR for _ in range(MAP_WIDTH)]
        fog_in.append(row)

    # initialise player
    player_in.clear()
    player_in['name'] = name
    player_in['x'] = 0
    player_in['y'] = 0
    player_in['copper'] = 0
    player_in['silver'] = 0
    player_in['gold'] = 0
    player_in['GP'] = 0
    player_in['day'] = 1 # changed from 0
    player_in['steps'] = 0
    player_in['turns'] = TURNS_PER_DAY

    # NEW BELOW
    player_in['capacity'] = 10
    player_in["pickaxe_level"] = 1
    player_in["valid_minable_ores"] = "C"
    # ^ uses first letters of minerals to check if player can mine
    player_in["torch_level"] = 1
    player_in["total_GP"] = 0

    clear_fog(fog_in=fog_in, player_in=player_in)

    print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")


# Template ✅✅✅
def draw_map(fog_in: list[list[str]],
             player_in: dict[str, str | int], current_map_in: list[list[str]]) -> None:
    """This function draws the entire map, covered by the fog if applicable.

    Parameters
    ----------
    fog_in : list[list[str]]
        input for GLOBAL fog variable (originally named fog) [or can be any 2D list]
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    current_map_in : list[list[str]]
        input for GLOBAL game map (originally named game_map)
    """

    player_pos = (player_in["y"], player_in["x"])

    used_portal_to_town: bool = player_pos != TOWN_POSITION and game_state == "town"
    walked_to_town: bool = player_pos == TOWN_POSITION and game_state == "town"

    output_text: str = f"\n+{"-"*MAP_WIDTH}+\n"
    for i in range(MAP_HEIGHT):
        row_text: str = ""
        for j in range(MAP_WIDTH):
            add_player: bool = False
            if used_portal_to_town or walked_to_town:
                add_player = (i,j) == TOWN_POSITION
            else: # Not in town
                add_player = (i,j) == (player_in["y"], player_in["x"])

            add_portal: bool = (i,j) == player_pos and used_portal_to_town

            if add_player:
                row_text += PLAYER_CHAR
            elif add_portal:
                row_text += "P"
            elif fog_in[i][j] == NON_FOG_CHAR:
                row_text += current_map_in[i][j]
            else:
                row_text += FOG_CHAR

        output_text += f"|{row_text}|\n"
    output_text += f"+{"-"*MAP_WIDTH}+"

    print(output_text)


# Template ✅✅✅
def draw_view(current_map_in: list[list[str]],
              player_in: dict[str, str | int], fog_in: list[list[str]]) -> None:
    """This function draws the 3x3 viewport. (adjusted by torch level)

    Parameters
    ----------
    current_map_in : list[list[str]]
        input for GLOBAL game map variable (originally named game_map)
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    fog_in : list[list[str]]
        input for GLOBAL fog (originally named fog)
    """

    print(f"DAY {player['day']}")
    x: int = player_in["x"]
    y: int = player_in["y"]
    sq_range: range = sq_increment_range(player_in["torch_level"])

    # Ensures that if torch is upgraded, viewport is affected too
    clear_fog(fog_in=fog_in, player_in=player_in)

    mine_rows: list[list[str]] = []

    for i in sq_range:
        row_n: int = y + i
        mine_row: str = ""
        for j in sq_range:
            col_n: int = x + j

            is_at_player_position: bool = are_equal(y1=y, y2=row_n, x1=x, x2=col_n)
            not_fog: bool = fog_in[row_n][col_n] == NON_FOG_CHAR

            if is_at_player_position: # Draws player
                mine_row += PLAYER_CHAR
            elif is_within(height=MAP_HEIGHT, width=MAP_WIDTH, x=col_n, y=row_n) and not_fog:
                mine_row += current_map_in[row_n][col_n]
            elif -1 <= row_n <= MAP_HEIGHT and -1 <= col_n <= MAP_WIDTH: # Draws walls
                mine_row += "#"
            else: # Uncomment this for a fixed area
                mine_row += " "
        if mine_row != "":
            mine_rows.append(mine_row)

    mine_rows = [f"|{row}|\n" for row in mine_rows]

    border_len: int = len(mine_rows[0]) - 3
    view: str= f"+{"-"*border_len}+\n"
    view += "".join(mine_rows)
    view += f"+{"-"*border_len}+\n"
    print(view)


# Template
def save_game(save_slot_number: int, current_map_in: list[list[str]],
              fog_in: list[list[str]], player_in: dict[str, str | int]) -> None:
    """This function saves the game.

    Parameters
    ----------
    save_slot_number : int
        Save slot number to save to determined by player.
    current_map_in : list[list[str]]
        input for GLOBAL game map (originally named game_map)
    fog_in : list[list[str]]
        input for GLOBAL fog (originally named fog)
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    # Saving current map
    save_list_to_txt(get_full_directory(slot_number=save_slot_number,
                                        data_name="current_map"), current_map_in)

    # Saving fog
    save_list_to_txt(get_full_directory(slot_number=save_slot_number,
                                        data_name="fog"), fog_in)

    # Saving player
    with open(get_full_directory(slot_number=save_slot_number, data_name="player"),
              "w", encoding="utf-8") as file:
        text_to_write: str = ""
        for key, value in player_in.items():
            text_to_write += f"{key},{value}\n"
        text_to_write = text_to_write[:len(text_to_write)-1] # Removes extra \n
        file.write(text_to_write)

    print(f"Saved to save slot {save_slot_number}")


# Template ✅✅✅
def load_game(save_slot_number: int, current_map_in: list[list[str]],
              fog_in: list[list[str]], player_in: dict[str, str | int]) -> bool:
    """This function loads the game.

    Parameters
    ----------
    save_slot_number : int
        Save slot number to load game from.
    current_map_in : list[list[str]]
        input for GLOBAL game map (originally named game_map)
    fog_in : list[list[str]]
        input for GLOBAL fog (originally named fog)
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)

    Returns
    -------
    bool
        Indicates if a (saved) game can be loaded.
    """

    try:
        # load map
        load_map(filename=get_full_directory(slot_number=save_slot_number, data_name="current_map"),
                  map_struct=current_map_in)

        # load fog
        load_map(filename=get_full_directory(slot_number=save_slot_number, data_name="fog"),
                  map_struct=fog_in)

        # load player
        player_in.clear()
        with open(get_full_directory(slot_number=save_slot_number, data_name="player"),
                  "r", encoding="utf-8") as file:
            data: list[str] = file.read().split("\n")

        for datum in data:
            split_datum: list[str] = datum.split(",")
            key, value = split_datum[0], split_datum[1]
            try: # For ints only
                value = int(value)
            except ValueError:
                pass
            player_in[key] = value

        # Sets the prices for that day.
        set_prices()

        return True
    except FileNotFoundError:
        print("There is not a saved game. Please start a new game.")
        return False


# ------------------------- Functions that show INFORMATION -------------------------


# Template
def show_information(menu_type: str, player_in: dict[str, str | int]) -> None:
    """This function shows the information for the player.

    Parameters
    ----------
    menu_type : str
        Specifies whether it is "town" or "mine" menu.
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)

    Raises
    ------
    ValueError
        Raised if value of menu_type is invalid
    """

    if menu_type not in ["town", "mine"]:
        raise ValueError(f"menu_type = {menu_type} is wrong. Check again.")

    print("\n----- Player Information -----")
    print(f"Name: {player_in["name"]}")

    if menu_type == "town":
        print(f"Portal position: {(player_in["x"], player_in["y"])}")
    else:
        print(f"Current position: {(player_in["x"], player_in["y"])}")

    print(f"Pickaxe level: {player_in['pickaxe_level']} ({minerals[player_in['pickaxe_level']-1]})")
    print(f"Torch level: {player_in["torch_level"]}")
    if menu_type == "mine":
        minerals.reverse()
        for mineral in minerals:
            print(f"{mineral.capitalize()}: {player_in[mineral]}")

    print("------------------------------")
    print(f"Load: {sum_ores_in_backpack(player_in=player_in)} / {player_in["capacity"]}")
    print("------------------------------")
    print(f"GP: {player_in["GP"]}")
    print(f"Steps taken: {player_in["steps"]}")
    print("------------------------------")


# Template
def show_main_menu() -> None:
    '''Shows main menu'''

    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
    # print("(H)igh scores") TODO
    print("(Q)uit")
    print("------------------")


# Template
def show_town_menu(player_in: dict[str, str | int]) -> None:
    """Shows town menu

    Parameters
    ----------
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    print()
    print(f"DAY {player_in['day']}")
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")


def show_shop_menu(show_pickaxes: bool,
                   show_torch: bool,
                   player_in: dict[str, str | int]) -> None:
    """Shows shop menu

    Parameters
    ----------
    show_pickaxes : bool
        Indicates whether to show pick axe price
    show_torch : bool
        Indicates whether to show torch price
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    print("\n----------------------- Shop Menu -------------------------")
    if show_pickaxes:
        pickaxe_price: int = pickaxe_prices[player_in["pickaxe_level"]-1]
        print(f"(P)ickaxe upgrade to Level {player_in['pickaxe_level']+1} "
              f"to mine {minerals[player_in['pickaxe_level']]} ore for {pickaxe_price} GP")

    if show_torch:
        torch_price: int = player_in["torch_level"] * TORCH_UPGRADE_MULTIPLIER
        print(f"(T)orch upgrade to Level {player_in['torch_level']+1} for {torch_price} GP")

    backpack_upgrade_price: int = player_in["capacity"] * BACKPACK_UPGRADE_CONSTANT
    print(f"(B)ackpack upgrade to carry {player_in["capacity"]+BACKPACK_UPGRADE_CONSTANT} items "
          f"for {backpack_upgrade_price} GP")
    print("(L)eave shop")
    print("-----------------------------------------------------------")
    print(f"GP: {player_in["GP"]}")
    print("-----------------------------------------------------------")


def show_mine_menu(player_in: dict[str, str | int],
                   fog_in: list[list[str]], current_map_in: list[list[str]]) -> None:
    """Shows mine menu

    Parameters
    ----------
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    fog_in : list[list[str]]
        input for GLOBAL fog (originally named fog)
    current_map_in : list[list[str]]
        input for GLOBAL game map (originally named game_map)
    """

    # print("---------------------------------------------------")
    # print(f"{f"DAY {player_in['day']}":^50}")
    # print("---------------------------------------------------")
    draw_view(current_map_in=current_map_in, player_in=player_in, fog_in=fog_in)
    print(f"Turns left: {player_in['turns']} {" "*4} Load: "
          f"{sum_ores_in_backpack(player_in=player_in)} / {player_in["capacity"]} "
          f"{" "*4} Steps: {player_in['steps']}")
    print("(WASD) to move")
    print("(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu")


def show_game_won(player_in: dict[str, str | int]) -> None:
    """Shows game win information

    Parameters
    ----------
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    print("-------------------------------------------------------------")
    print(f"Woo-hoo! Well done, Cher, you have {player_in["GP"]} GP!")
    print("You now have enough to retire and play video games every day.")
    print(f"And it only took you {player_in["day"]} day(s) and "
          f"{player_in["steps"]} steps! You win!")
    print("-------------------------------------------------------------")


# ------------------------- Various functions that are used in Menus -------------------------
def archive_data(player_in) -> None:
    """Saves the data of a player that has won the game to archive file."""
    # FIXME
    with open(ARCHIVE_FILE_NAME, "w", encoding="utf-8") as f:
        text_to_write: str = ""
        for record in high_score_records:
            text_to_write += f"{record},{high_score_records[record]["day"]},{high_score_records[record]["steps"]},{high_score_records[record]["total_GP"]}\n"
            # print(record)
        # print(player_in)
        text_to_write += f"{player_in["name"]},{player_in["day"]},{player_in["steps"]},{player_in["total_GP"]}\n"
        # print("Added player")
        f.write(text_to_write)


def new_day(player_in: dict[str, str | int]) -> None:
    """When a new day passes, does the following.

    Parameters
    ----------
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    player_in["turns"] = TURNS_PER_DAY
    player_in["day"] += 1
    set_prices()


def sum_ores_in_backpack(player_in: dict[str, str | int]) -> int:
    """Returns the sum of the quantity of minerals in backpack.

    Parameters
    ----------
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)

    Returns
    -------
    int
        number of ores in backpack
    """

    return sum(player_in[mineral] for mineral in minerals)


def set_prices() -> None:
    '''Sets the prices for minerals. To be called at the start of a new day.'''
    current_prices.clear()
    for mineral in minerals:
        current_prices[mineral] = randint(prices[mineral][0], prices[mineral][1])


def sell_ores(player_in: dict[str, str | int]) -> bool:
    """Sells ores. Checks if player has won the game.

    Parameters
    ----------
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)

    Returns
    -------
    bool
        Specifies whether to return to main menu or not.
    """

    have_sold_stuff: bool = False

    # Sell ores
    for mineral in minerals:
        if player_in[mineral] > 0:
            # print(current_prices)
            gp_sold: int = player_in[mineral] * current_prices[mineral]
            print(f"You sell {player_in[mineral]} {mineral} ore for {gp_sold} GP.")
            player_in["GP"] += gp_sold
            player_in["total_GP"] += gp_sold
            player_in[mineral] = 0
            have_sold_stuff = True

    if have_sold_stuff:
        print(f"You now have {player_in["GP"]} GP!")
    if player_in["GP"] >= WIN_GP:
        show_game_won(player_in=player_in)
        save_game(save_slot_number=current_save_slot,
                  current_map_in=current_map, fog_in=fog, player_in=player_in)
        archive_data(player_in=player_in)
        return True
    return False


def is_ore_minable(ore_found_input: str, player_in: dict[str, str | int]) -> bool:
    """Checks if the ore found can be mined depending on pickaxe level.

    Parameters
    ----------
    ore_found_input : str
        Capital letter of ore found
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)

    Returns
    -------
    bool
        Indicates of ore is minable based on pickaxe level.
    """

    if ore_found_input in player_in["valid_minable_ores"]:
        # print("You can mine this!")
        return True
    print(f"Your pickaxe level ({player_in['pickaxe_level']}) is "
        f"too low, so you cannot mine {mineral_names[ore_found_input]}.")
    return False

# ✅✅✅ (SHOULD BE DONE)
def valid_move_checker(direction: str, move_value: int,
                       player_in: dict[str, str | int],
                       current_map_in: list[list[str]]) -> bool:
    """Checks if a WASD move is valid.

    Parameters
    ----------
    direction : str
        direction of movement; can be "x" or "y"
    move_value : int
        magnitude of movement; can be -1 or 1
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    current_map_in : list[list[str]]
        input for GLOBAL game map (originally named game_map)

    Returns
    -------
    bool
        Indicates if a WASD move is valid.

    Raises
    ------
    ValueError
        Raised if value of direction is not "x" or "y".
    ValueError
        Raised if value of direction is not -1 or 1.
    """

    # Input checks
    if direction not in ["x", "y"]:
        raise ValueError(f"{direction} is an invalid value for direction; must be 'x' or 'y'")
    if move_value not in [1,-1]:
        raise ValueError(f"{move_value} is an invalid value for move_value; must be 1 or -1")

    player_in["turns"] -= 1
    player_in["steps"] += 1

    # Determines new hypothetical position and square
    position_to_check: dict[str, int] = {"x": player_in["x"], "y": player_in["y"]}
    position_to_check[direction] += move_value
    # print(f"New position: {position_to_check["x"]}, {position_to_check['y']}")

    # Checks if hypothetical position is within map boundaries
    if not is_within(height=MAP_HEIGHT, width=MAP_WIDTH,
                     x=position_to_check["x"], y=position_to_check["y"]):
        print("You can't go that way.")
        return False

    # Determines new hypothetical square
    square_to_check: str = current_map_in[position_to_check["y"]][position_to_check["x"]]

    # Checks if player's backpack is full and if the square to be stepped on is a mineral
    is_backpack_full: bool = sum_ores_in_backpack(player_in=player_in) == player_in["capacity"]
    is_next_square_a_mineral: bool = square_to_check in mineral_names

    if is_backpack_full and is_next_square_a_mineral:
        print("You can't carry any more, so you can't go that way.")
        return False
    if is_next_square_a_mineral:
        return is_ore_minable(ore_found_input=square_to_check, player_in=player_in)

    return True # Move to a non-ore square


def process_ore_into_backpack(ore_found_input: str, player_in: dict[str, str | int]) -> None:
    """Adds the pieces of ore found into the backpack depending on backpack capacity.

    Parameters
    ----------
    ore_found_input : str
        Capital letter of ore found
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    remaining_space_in_backpack: int = player_in["capacity"] - sum_ores_in_backpack(player_in=player_in)
    mineral_name: str = mineral_names[ore_found_input]
    pieces_found: int = randint(pieces_per_node[mineral_name][0], pieces_per_node[mineral_name][1])

    if pieces_found <= remaining_space_in_backpack:
        print(f"You mined {pieces_found} piece(s) of {mineral_name}.")
        player_in[mineral_names[ore_found_input]] += pieces_found
    else:
        print(f"You mined {pieces_found} piece(s) of {mineral_name}.")
        print(f"...but you can only carry {remaining_space_in_backpack} more piece(s)!")
        player_in[mineral_names[ore_found_input]] += remaining_space_in_backpack

# ✅✅✅
def movement_in_mine(mine_menu_choice_input: str, player_in: dict[str, str | int],
                     current_map_in: list[list[str]],
                     fog_in: list[list[str]]) -> None:
    """Simulates movement in the mine (WASD input in Mine Menu)

    Parameters
    ----------
    mine_menu_choice_input : str
        User's selection in mine menu.
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    current_map_in : list[list[str]]
        input for GLOBAL game map (originally named game_map)
    fog_in : list[list[str]]
        input for GLOBAL fog (originally named fog)

    Returns
    -------
    None
        To simply exit the function.
    """

    global game_state

    direction: str = WASD_TO_DIRECTION_AND_MOVE_VALUE[mine_menu_choice_input]["direction"]
    move_value: int = WASD_TO_DIRECTION_AND_MOVE_VALUE[mine_menu_choice_input]["move_value"]

    if valid_move_checker(direction=direction, move_value=move_value,
                          player_in=player_in, current_map_in=current_map_in):
        player_in[direction] += move_value # Update player position

        clear_fog(fog_in=fog_in, player_in=player_in)

        square_stepped: str = current_map_in[player_in["y"]][player_in["x"]]

        if square_stepped in mineral_names: # if an ore was stepped on
            process_ore_into_backpack(ore_found_input=square_stepped, player_in=player_in)
            current_map_in[player_in["y"]][player_in["x"]] = " " # Remove ore vein
        elif square_stepped == "T":
            print("You returned to town.")
            game_state = "town"
            return None

    if player_in["turns"] == 0:
        print("You are exhausted.\n"
            "You place your portal stone here and zap back to town.")
        game_state = "town"
        return None
    return None


# ------------------------- Menu Functions -------------------------


def main_menu(current_map_in: list[list[str]], fog_in: list[list[str]],
              player_in: dict[str, str | int]) -> None:
    """Simulates the interaction of main menu.

    Parameters
    ----------
    current_map_in : list[list[str]]
        input for GLOBAL game map (originally named game_map)
    fog_in : list[list[str]]
        input for GLOBAL fog (originally named fog)
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    global current_save_slot
    global game_state
    game_state = "main"

    while True:
        show_main_menu()
        main_menu_choice: str = validate_input("Your choice? ", r"^[nlq]$", True)

        if main_menu_choice == "n":
            initialize_game(current_map_in=current_map_in, fog_in=fog_in,
                            player_in=player_in)
            save_game(save_slot_number=current_save_slot,
                      current_map_in=current_map_in, fog_in=fog_in, player_in=player_in)
            load_game(save_slot_number=current_save_slot,
                      current_map_in=current_map_in, fog_in=fog_in, player_in=player_in)
            game_state = "town"
            break
        if main_menu_choice == "l":
            save_slots_written_already: list[str] = [str(n) for n in
                                                     find_written_slots(mode="load")]
            if len(save_slots_written_already) == 0:
                print("There has not been a save slot written to. Please create a new save slot.")
                continue

            regex = "".join(save_slots_written_already)
            regex = create_regex(valid_char=regex)

            current_save_slot = int(validate_input("Your choice? ", regex, True))
            loaded_success: bool = load_game(save_slot_number=current_save_slot,
                                             current_map_in=current_map_in,
                                             fog_in=fog_in, player_in=player_in)
            if not loaded_success:
                continue
            game_state = "town"
            print("Game loaded.")
            break
        if main_menu_choice == "q":
            game_state = "exit"
            break


def buy(player_in: dict[str, str | int], option: str, price: int) -> None:
    """Simulates buying."""
    if player_in["GP"] < price:
        print("You don't have enough GP!")
        return None

    player_in["GP"] -= price

    if option == "p":
        player_in["valid_minable_ores"] += minerals[player_in['pickaxe_level']][0].upper()
        player_in["pickaxe_level"] += 1
        print("Congratulations! "
                f"You can now mine {minerals[player_in['pickaxe_level']-1]}!")
    elif option == "b":
        player_in["capacity"] += BACKPACK_UPGRADE_CONSTANT
        print(f"Congratulations! You can now carry {player_in["capacity"]} items!")
    else:
        player_in["torch_level"] += 1
        print(f"Congratulations! Your torch level is now level {player_in['torch_level']}.")
    return None


def shop_menu(player_in: dict[str, str | int]) -> None:
    """Simulates the interaction of shop menu

    Parameters
    ----------
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    while True:
        # Determine valid options
        options: str = "bl"
        show_pickaxes: bool = False
        show_torch: bool = False

        if player_in["pickaxe_level"] <= len(pickaxe_prices):
            options += "p"
            show_pickaxes = True
        if player_in["torch_level"] < TORCH_LEVEL_LIMIT:
            options += "t"
            show_torch = True
        show_shop_menu(show_pickaxes=show_pickaxes, show_torch=show_torch, player_in=player_in)
        shop_menu_choice: str = validate_input("Your choice? ", create_regex(options), True)

        if shop_menu_choice == "p":
            price: int = pickaxe_prices[player_in["pickaxe_level"]-1]
            buy(player_in=player_in, option=shop_menu_choice, price=price)
        elif shop_menu_choice == "b":
            price: int = player_in["capacity"] * BACKPACK_UPGRADE_CONSTANT
            buy(player_in=player_in, option=shop_menu_choice, price=price)
        elif shop_menu_choice == "t":
            price: int = player_in["torch_level"] * TORCH_UPGRADE_MULTIPLIER
            buy(player_in=player_in, option=shop_menu_choice, price=price)
        else:
            break


def mine_menu(current_map_in: list[list[str]], fog_in: list[list[str]],
              player_in: dict[str, str | int]) -> None:
    """Simulates the interaction of mine menu.

    Parameters
    ----------
    current_map_in : list[list[str]]
        input for GLOBAL game map (originally named game_map)
    fog_in : list[list[str]]
        input for GLOBAL fog (originally named fog)
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """

    global game_state
    game_state = "mine" # "mine" is not used often now

    print("\n---------------------------------------------------")
    print(f"{f"DAY {player_in['day']}":^50}")
    print("---------------------------------------------------")

    while True:
        show_mine_menu(player_in=player_in, fog_in=fog_in, current_map_in=current_map_in)
        mine_menu_choice: str = validate_input("Action? ", r"^[wasdmipq]$", True)
        print("\n------------------------------------------------------")

        if mine_menu_choice in "wasd":
            movement_in_mine(mine_menu_choice_input=mine_menu_choice,
                             player_in=player_in, current_map_in=current_map_in, fog_in=fog_in)
            if game_state == "town":
                new_day(player_in=player_in)
                break
        elif mine_menu_choice == "m":
            draw_map(fog_in=fog_in, player_in=player_in, current_map_in=current_map_in)
        elif mine_menu_choice == "i":
            show_information(menu_type="mine", player_in=player_in)
        elif mine_menu_choice == "p":
            print("You place your portal stone here and zap back to town.")
            game_state = "town"
            new_day(player_in=player_in)
            break
        else:
            game_state = "main"
            break


def town_menu(current_map_in: list[list[str]], fog_in: list[list[str]],
              player_in: dict[str, str | int]) -> None:
    """Simulates the interaction of town menu.

    Parameters
    ----------
    current_map_in : list[list[str]]
        input for GLOBAL game map (originally named game_map)
    fog_in : list[list[str]]
        input for GLOBAL fog (originally named fog)
    player_in : dict[str, str  |  int]
        input for GLOBAL player (originally named player)
    """    '''Simulates the interaction of town menu'''
    # print(current_prices)

    global game_state
    game_state = "town"

    while True:
        return_to_main_menu: bool = sell_ores(player_in=player_in)
        if return_to_main_menu:
            break

        show_town_menu(player_in=player_in)
        town_menu_choice: str = validate_input("Your choice? ", r"^[bimevq]$", True)

        if town_menu_choice == "b":
            shop_menu(player_in=player_in)
        elif town_menu_choice == "i":
            show_information(menu_type="town", player_in=player_in)
        elif town_menu_choice == "m":
            draw_map(fog_in=fog_in, player_in=player_in, current_map_in=current_map_in)
        elif town_menu_choice == "e":
            mine_menu(player_in=player_in, current_map_in=current_map_in, fog_in=fog_in)

            if game_state == "main":
                break
        elif town_menu_choice == "v":
            save_game(save_slot_number=current_save_slot,
                  current_map_in=current_map_in, fog_in=fog_in, player_in=player_in)
        else:
            break


#--------------------------- Miscellaneous ---------------------------
def create_save_folders() -> None:
    """Creates save slot folders. Ensures they exist in working directory.
    Source: https://www.geeksforgeeks.org/python/create-a-directory-in-python/
    """

    for i in range(1, SAVE_SLOT_QUANTITY+1):
        full_dir_path: str = get_save_slot_dir(number=i)
        try: # The exceptions are only for debugging
            os.mkdir(full_dir_path)
        except FileExistsError:
            pass
        except PermissionError:
            assert False, f"Permission denied: Unable to create '{full_dir_path}'."
        except Exception as exp:
            # assert False, f"An error occurred while attempting creating {full_dir_path}: {exp}"
            print(exp) # FIXME IN DEBUG MODE


def load_high_scores() -> None: # FIXME
    """Reads the past players nfo who have have
    won (to be used to show high scores)"""

    with open(ARCHIVE_FILE_NAME, "r", encoding="utf-8") as f:
        info: str = f.read().strip()
    if info != "":
        data = info.split("\n")
        for i in range(len(data)):
            data[i] = data[i].split(",")
            high_score_records[data[i][0]] = {"day": data[i][1], "steps": data[i][2], "total_GP": data[i][3]}
    # print(high_score_records)


#--------------------------- MAIN GAME ---------------------------
def main():
    """Main game

    Raises
    ------
    ValueError
        Raised if value of game_state is invalid.
    """

    # Create file that archives past players' data
    try:
        f = open(ARCHIVE_FILE_NAME, "r", encoding="utf-8")
    except FileNotFoundError:
        f = open(ARCHIVE_FILE_NAME, "w", encoding="utf-8")
    f.close()

    create_save_folders()

    # game_state: str = 'main'
    print("---------------- Welcome to Sundrop Caves! ----------------")
    print("You spent all your money to get the deed to a mine, a small")
    print("  backpack, a simple pickaxe and a magical portal stone.")
    print()
    print(f"How quickly can you get the {WIN_GP} GP you need to retire")
    print("  and live happily ever after?")
    print("-----------------------------------------------------------")

    while True: # MAIN LOOP
        load_high_scores()
        main_menu(current_map_in=current_map, fog_in=fog, player_in=player)

        if game_state == "exit":
            break
        if game_state == "town":
            town_menu(player_in=player, current_map_in=current_map, fog_in=fog)
        else:
            raise ValueError(f"game_state cannot be {game_state}")

    print("Thanks for playing")


if __name__=="__main__":
    main()
