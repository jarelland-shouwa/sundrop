'''
# TODO The program should have sufficient comments,
# which includes your name, class, date, overall
# description of what the program does, as well
# as the description of the functions.
'''

from random import randint
import os
import re

player: dict[str: (str, int)] = {}
game_map: list[list[str]] = []
current_map: list[list[str]] = []

MAP_WIDTH: int = 0
MAP_HEIGHT: int = 0

TURNS_PER_DAY: int = 20
WIN_GP: int = 500

minerals: list[str] = ['copper', 'silver', 'gold']
mineral_names: dict[str: str] = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_prices: list[int] = [50, 150]

prices: dict[str: tuple[int]] = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

# NEW
pieces_per_node: dict[str: tuple[int]] = {}
pieces_per_node['copper'] = (1, 5)
pieces_per_node['silver'] = (1, 3)
pieces_per_node['gold'] = (1, 2)

# Dynamic
current_prices: dict[str: int] = {}

current_save_slot: int = 1 # Needs to be globalised
SAVE_SLOT_QUANTITY: int = 5

WASD_TO_DIRECTION_AND_MOVE_VALUE: dict[str: dict[str: str]]= {
    "w": {"direction": "y", "move_value": -1},
    "a": {"direction": "x", "move_value": -1},
    "s": {"direction": "y", "move_value": 1},
    "d": {"direction": "x", "move_value": 1}}

SAVE_SLOT_DIRECTORY_PREFIX = "saves/save_slot"
# E.g. saves/save_slot_1 (to be done by get_save_slot_dir)

# ------------------------- GENERAL Functions -------------------------


# Assumes that input will be a SINGLE LETTER
def validate_input(message: str, regex: str) -> str:
    '''Uses a regular expression to validate input.'''
    while True:
        user_input: str = input(message).lower()
        if re.match(regex, user_input):
            return user_input
        if user_input == "":
            print("Please enter a valid input instead of nothing.")
        else:
            print(f"{user_input} is invalid. Please enter a valid input.")


def save_list_to_txt(filename: str, input_list: list) -> None:
    '''Saves a list into a text file.'''
    save_file_map = open(filename, "w", encoding="utf-8")
    text_to_write: str = ""
    for row in input_list:
        for element in row:
            text_to_write += element
        text_to_write += "\n"
    text_to_write = text_to_write[:len(text_to_write)-1] # remove extra \n
    save_file_map.write(text_to_write)
    save_file_map.close()


def is_within(height: int, width: int, x: int, y: int) -> bool:
    '''Checks if a position is within the boundaries of a 2D list.'''
    return 0 <= y <= (height-1) and 0 <= x <= (width-1)


def are_equal(y1: int, y2: int, x1: int, x2: int) -> bool:
    '''Checks if two positions are equal.'''
    return x1 == x2 and y1 == y2


def determine_square_grid_in_list(x: int, y: int,
                                  list_height: int,
                                  list_width: int) -> tuple[
                                      list[dict[str: int]],
                                      list[dict[str: int]]]:
    # FIXME Currently the invalid_positions output is not being used.
    '''Returns positions that are within a square of side 3 as the (x,y) the centre.
    I.e. positions that are within a Manhattan Distance of 2 units, exclduing (x,y)
    
    Output: valid_positions, invalid_positions
    valid_positions = [pos_dict_1, pos_dict_2, pos_dict_3, ...]
    invalid_positions = [pos_dict_1, pos_dict_2, pos_dict_3, ...]'''
    valid_positions: list[dict[str: int]] = []
    invalid_positions: list[dict[str: int]] = []
    for i in range(-1, 2):
        row_n: int = y + i
        for j in range(-1,2):
            col_n: int = x + j

            # Excludes the centre of the square
            is_centre: bool = are_equal(y1=y, y2=row_n, x1=x, x2=col_n)

            if is_within(height=list_height, width=list_width, x=col_n, y=row_n) and not is_centre:
                valid_positions.append({"x": col_n, "y": row_n})
            else:
                invalid_positions.append({"x": col_n, "y": row_n})
    return valid_positions, invalid_positions


def create_regex(valid_char: str) -> str:
    '''Creates a raw expression for regex that only accpets certain single characters.'''
    return rf"^[{valid_char}]$"


def get_full_directory(slot_number: int, data_name: str) -> str:
    '''Retruns the full directory path for a txt file to be saved in a save slot.'''
    directory_name = get_save_slot_dir(number=slot_number)
    return f"{directory_name}/save_{slot_number}_{data_name}.txt"

# ------------------------- Initialise-, Load-, Save-related Functions -------------------------


def find_written_slots(mode: str) -> list[int]:
    '''
    Checks all of the save slot folders to see if they are empty or not.
    Takes in a mode for different print messages.
    Returns a list of save slots that has data already written to it.
    '''
    if mode not in ["save", "load"]:
        raise ValueError(f"{mode} is invalid. Valid: {["save", "load"]}. Please check again.")

    written_colour, empty_colour = 91, 92
    if mode == "save":
        save_slot_listing_text = "Select a save slot to save to.\n"
    elif mode == "load":
        save_slot_listing_text = "Select a save slot to load from.\n"
        written_colour = 92
        empty_colour = 91

    written_slots: list[int] = []
    for i in range(1, SAVE_SLOT_QUANTITY+1):
        try:
            directory: list[str] = os.listdir(get_save_slot_dir(number=i))
        except FileNotFoundError:
            assert False, f"\033[91m{f"Slot {i}: EMPTY ; FileNotFoundError; Please check that this folder has been created."}\033[00m"
        else:
            if len(directory) != 0:
                # TODO check that exact files with
                # naming conventions are included (to account for deleted fies)
                written_slots.append(i)
                save_slot_listing_text += f"\033[{written_colour}m{f"Slot {i}: HAS BEEN WRITTEN TO\n"}\033[00m"
            else:
                save_slot_listing_text += f"\033[{empty_colour}m{f"Slot {i}: EMPTY ; No files in save folder\n"}\033[00m"

    # Lists whether a save slot is empty or has data already written to it.
    print(save_slot_listing_text)
    return written_slots


def choose_new_save_slot() -> int:
    '''Allows choosing of save slot to begin a NEW game. Returns save slot choice'''
    written_slots: list[int] = find_written_slots(mode="save")

    # Creating regex for input validation based on number of save slots.
    separator = "|"
    regex: str = separator.join([str(i) for i in list(range(1,SAVE_SLOT_QUANTITY+1))])
    regex = create_regex(valid_char=regex)

    # Asking user for desired save slot choice
    while True:
        save_slot_choice: int = int(validate_input("Your choice? ", regex))
        if save_slot_choice in written_slots:
            confirmation_choice: str = validate_input(f"Are you sure? This will overwrite save "
                                                 f"slot {save_slot_choice}. "
                                                 "Your choice (y/n)? ", r"^[y|n]$")
            if confirmation_choice == "n":
                print(f"You chose not to overwrite save slot {save_slot_choice}")
                continue
        break

    return save_slot_choice


def load_map(filename: str, map_struct: list) -> None:
    '''
    Loads a map structure (a nested list) from a file.
    Updates MAP_WIDTH and MAP_HEIGHT.
    Saves data to map_struct.'''
    map_file = open(filename, 'r', encoding="utf-8")
    global MAP_WIDTH
    global MAP_HEIGHT

    map_struct.clear()

    lines: list[str] = map_file.read().split("\n")
    for line in lines:
        line: list[str] = list(line)
        map_struct.append(line)

    MAP_WIDTH = len(map_struct[0])
    MAP_HEIGHT = len(map_struct)

    map_file.close()


def initialize_game(game_map_in, current_map_in, player_in) -> None:
    '''Initiliases game_map, current_map and player information
    Parameters:
    - game_map_in : game map structure (originally named game_map)'''
    global current_save_slot

    current_save_slot = choose_new_save_slot()
    name: str = validate_input("Greetings, miner! What is your name? ", r"^.+$")

    # initialise map
    game_map_in.clear()
    try:
        load_map(filename="level1.txt", map_struct=game_map_in)
    except FileNotFoundError:
        print("FileNotFoundError; Please check that the level map exists again.")

    # Create current map WITH fog TODO Create a function that does this
    current_map_in.clear()
    for _ in range(MAP_HEIGHT):
        row: list[str] = ["?" for _ in range(MAP_WIDTH)]
        current_map_in.append(row)
    current_map_in[0][0] = "M"

    # initialize player
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

    print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")


def draw_map(map_in, in_town: bool) -> None:
    '''This function draws the entire map, covered by the fog if applicable.
    Accounts for special cases:
    1. Player in town
    2. Player in town & Portal stone placed'''

    output_text: str = f"\n+{"-"*MAP_WIDTH}+\n"
    for i in range(MAP_HEIGHT):
        row_text: str = ""
        for j in range(MAP_WIDTH):
            if in_town and (i,j) == (0, 0): # Special case 1; # hard coded town position
                row_text += "M"
                continue
            if in_town and map_in[i][j] == "M": # Special case 2
                row_text += "P"
                continue

            row_text += map_in[i][j]
        output_text += f"|{row_text}|\n"
    output_text += f"+{"-"*MAP_WIDTH}+"

    print(output_text)


def draw_view(map_in, player_in) -> None:
    '''This function draws the 3x3 viewport'''
    print(f"DAY {player['day']}")
    x: int = player_in["x"]
    y: int = player_in["y"]

    view_to_print: str = "+---+\n"
    for i in range(-1, 2):
        row_n: int = y + i
        view_to_print += "|"
        for j in range(-1,2):
            col_n: int = x + j

            is_at_player_position: bool = are_equal(y1=y, y2=row_n, x1=x, x2=col_n)

            if is_at_player_position: # Draws player
                view_to_print += "M"
            elif is_within(height=MAP_HEIGHT, width=MAP_WIDTH, x=col_n, y=row_n):
                view_to_print += map_in[row_n][col_n]
            else: # Draws wall of mine
                view_to_print += "#"
        view_to_print += "|\n"
    view_to_print += "+---+"
    print(view_to_print)


def get_save_slot_dir(number: int) -> str:
    '''Returns save slot directory name based on slot number.'''
    return f"{SAVE_SLOT_DIRECTORY_PREFIX}_{number}"


def save_game(save_slot_number: int, game_map_in, current_map_in, player_in) -> None:
    '''This function saves the game'''
    # Saving game map
    save_list_to_txt(get_full_directory(slot_number=save_slot_number,
                                        data_name="map"), game_map_in)

    # Saving current map
    save_list_to_txt(get_full_directory(slot_number=save_slot_number,
                                        data_name="current_map"), current_map_in)

    # save fog TODO

    # Saving player info
    with open(get_full_directory(slot_number=save_slot_number, data_name="player"),
              "w", encoding="utf-8") as file:
        text_to_write: str = ""
        for key, value in player_in.items():
            if isinstance(value, (int, float, str)):
                text_to_write += f"{key},{value}\n"
        text_to_write = text_to_write[:len(text_to_write)-1] # Removes extra \n
        file.write(text_to_write)

    print(f"Saved to save slot {save_slot_number}")


def load_game(save_slot_number: int, game_map_in, current_map_in, player_in) -> bool:
    '''This function loads the game.'''
    try:
        # load map
        load_map(filename=get_full_directory(slot_number=save_slot_number, data_name="map"),
                  map_struct=game_map_in)
        load_map(filename=get_full_directory(slot_number=save_slot_number, data_name="current_map"),
                  map_struct=current_map_in)

        # load player
        player_in.clear()
        with open(get_full_directory(slot_number=save_slot_number, data_name="player"),
                  "r", encoding="utf-8") as file:
            data: list[str] = file.read().split("\n")

        for datum in data:
            datum: list[str] = datum.split(",")
            try: # typecasting strings into floats and integers
                if "." in datum[1]:
                    datum[1] = float(datum[1])
                else:
                    datum[1] = int(datum[1])
                player_in[datum[0]] = datum[1]
            except ValueError: # for strings
                player_in[datum[0]] = datum[1]

        # Sets the prices for that day.
        set_prices()

        return True
    except FileNotFoundError:
        print("There is not a saved game. Please start a new game.")
        return False


# ------------------------- Functions that show INFORMATION -------------------------


def show_information(menu_type: str, player_in) -> None:
    '''This function shows the information for the player.'''
    print("\n----- Player Information -----")
    print(f"Name: {player_in["name"]}")
    assert menu_type in ["town", "mine"], f"menu_type = {menu_type} is wrong. check again"

    if menu_type == "town":
        print(f"Portal position: {(player_in["x"], player_in["y"])}")
    else:
        print(f"Current position: {(player_in["x"], player_in["y"])}")
    print(f"Pickaxe level: {player_in['pickaxe_level']} ({minerals[player_in['pickaxe_level']-1]})")
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


def show_main_menu() -> None:
    '''Shows main menu'''
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
    # print("(H)igh scores")
    print("(Q)uit")
    print("------------------")


def show_town_menu(player_in) -> None:
    '''Shows town menu'''
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


def show_shop_menu(show_pickaxes: bool, player_in) -> None: # gp: int parameter
    '''Shows shop menu'''
    print("\n----------------------- Shop Menu -------------------------")
    if show_pickaxes:
        pickaxe_price: int = pickaxe_prices[player_in["pickaxe_level"]-1]
        print(f"(P)ickaxe upgrade to Level {player_in['pickaxe_level']+1} "
              f"to mine {minerals[player_in['pickaxe_level']]} ore for {pickaxe_price} GP")

    backpack_upgrade_price: int = player_in["capacity"] * 2
    print(f"(B)ackpack upgrade to carry {player_in["capacity"]+2} items "
          f"for {backpack_upgrade_price} GP")
    print("(L)eave shop")
    print("-----------------------------------------------------------")
    print(f"GP: {player_in["GP"]}")
    print("-----------------------------------------------------------")


def show_mine_menu(player_in) -> None:
    '''Shows mine menu'''
    print("---------------------------------------------------")
    print(f"{f"DAY {player_in['day']}":^50}")
    print("---------------------------------------------------")
    draw_view(map_in=current_map, player_in=player_in)
    print(f"Turns left: {player_in['turns']} {" "*4} Load: "
          f"{sum_ores_in_backpack(player_in=player_in)} / {player_in["capacity"]} "
          f"{" "*4} Steps: {player_in['steps']}")
    print("(WASD) to move")
    print("(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu")


def show_game_won(player_in) -> None:
    '''Shows game win information'''
    print("-------------------------------------------------------------")
    print(f"Woo-hoo! Well done, Cher, you have {player_in["GP"]} GP!")
    print("You now have enough to retire and play video games every day.")
    print(f"And it only took you {player_in["day"]} days and "
          f"{player_in["steps"]} steps! You win!")
    print("-------------------------------------------------------------")


# ------------------------- Various functions that are used in Menus -------------------------


def new_day(player_in) -> None:
    '''When a new day passes, does the following.'''
    player_in["turns"] = TURNS_PER_DAY
    player_in["day"] += 1
    set_prices()


def sum_ores_in_backpack(player_in) -> int:
    '''Returns the sum of the quantity of minerals in backpack.'''
    return sum(player_in[mineral] for mineral in minerals)


def set_prices() -> None:
    '''Sets the prices for minerals. To be called at the start of a new day.'''
    current_prices.clear()
    for mineral in minerals:
        current_prices[mineral] = randint(prices[mineral][0], prices[mineral][1])


def sell_ores(player_in) -> bool:
    '''Sells ores. Checks if player has won the game.
    Returns bool value that specifies whether to return to main menu or not.'''
    have_sold_stuff: bool = False
    for mineral in minerals:
        if player_in[mineral] > 0:
            # print(current_prices)
            gp_sold: int = player_in[mineral] * current_prices[mineral]
            print(f"You sell {player_in[mineral]} {mineral} ore for {gp_sold} GP.")
            player_in["GP"] += gp_sold
            player_in[mineral] = 0
            have_sold_stuff = True
    if have_sold_stuff:
        print(f"You now have {player_in["GP"]} GP!")
    if player_in["GP"] >= WIN_GP:
        show_game_won(player_in=player_in)
        save_game(save_slot_number=current_save_slot,
                  game_map_in=game_map, current_map_in=current_map, player_in=player_in)
        return True
    return False


def is_ore_minable(ore_found_input: str, player_in) -> bool:
    '''Checks if the ore found can be mined depending on pickaxe level.'''
    if ore_found_input in player_in["valid_minable_ores"]:
        print("You can mine this!")
        return True
    print(f"Your pickaxe level ({player_in['pickaxe_level']}) is "
        f"too low, so you cannot mine {mineral_names[ore_found_input]}.")
    return False


def valid_move_checker(direction: str, move_value: int, player_in, current_map_in) -> bool:
    '''Checks if a move of WASD is valid.
    direction = "x" or "y"
    move_value = -1 or 1'''
    # Input checks
    if direction not in ["x", "y"]:
        raise ValueError(f"{direction} is an invalid value for direction")
    if move_value not in [1,-1]:
        raise ValueError(f"{move_value} is an invalid value for move_value")

    player_in["turns"] -= 1
    player_in["steps"] += 1

    # Determines new hypothetical position and square
    position_to_check: dict[str: int] = {"x": player_in["x"], "y": player_in["y"]}
    position_to_check[direction] += move_value
    # print(f"{position_to_check["x"]}, {position_to_check['y']}")

    # Checks if hypothetical position is within map boundaries
    if not is_within(height=MAP_HEIGHT, width=MAP_WIDTH,
                     x=position_to_check["x"], y=position_to_check["y"]):
        print("You can't go that way.")
        return False

    # Determines new hypothetical square
    square_to_check: str = current_map_in[position_to_check["y"]][position_to_check["x"]]

    # Checks if player's backpack is full and if the square to be stepped on is a mineral
    is_player_backpack_full: bool = sum_ores_in_backpack(player_in=player_in) == player_in["capacity"]
    is_next_square_a_mineral: bool = square_to_check in list(key for key in mineral_names)
    if is_player_backpack_full and is_next_square_a_mineral:
        print("You can't carry any more, so you can't go that way.")
        return False

    if square_to_check in mineral_names:
        return is_ore_minable(ore_found_input=square_to_check, player_in=player_in)

    return True


def process_ore_into_backpack(ore_found_input: str, player_in) -> None:
    '''Adds the pieces of ore found into the backpack depending on backpack capacity.'''
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


def movement_in_mine(mine_menu_choice_input: str, player_in, game_map_in, current_map_in) -> bool:
    '''Simulates movement in the mine (WASD input in Mine Menu)'''
    direction: str = WASD_TO_DIRECTION_AND_MOVE_VALUE[mine_menu_choice_input]["direction"]
    move_value: int = WASD_TO_DIRECTION_AND_MOVE_VALUE[mine_menu_choice_input]["move_value"]

    if valid_move_checker(direction=direction, move_value=move_value,
                          player_in=player_in, current_map_in=current_map_in):
        # print("YAY you can move!")
        # Restore square to be stepped away (was previously covered by player avatar)
        current_map_in[player_in["y"]][player_in["x"]] = game_map_in[player_in["y"]][player_in["x"]]

        player_in[direction] += move_value # Update player position

        # Update positions within 3x3 square from player;
        # update current_map using game_map (clears fog)
        positions_to_update: list[dict[str: int]] = determine_square_grid_in_list(x=player_in["x"],
                                                            y=player_in["y"],
                                                            list_height=MAP_HEIGHT,
                                                            list_width=MAP_WIDTH)[0]
        for position in positions_to_update:
            y = position["y"]
            x = position["x"]
            current_map_in[y][x] = game_map_in[y][x]

        square_stepped: str = current_map_in[player_in["y"]][player_in["x"]]

        if square_stepped in mineral_names: # if an ore was stepped on
            ore_found: str = current_map_in[player_in["y"]][player_in["x"]]
            # print(f"Ore found: {ore_found}")
            process_ore_into_backpack(ore_found_input=ore_found, player_in=player_in)
            game_map_in[player_in["y"]][player_in["x"]] = " " # Remove ore vein
        elif square_stepped == "T":
            # If you step on the
            # 'T' square at (0, 0), you will return to town
            print("You returned to town.")
            return True

        current_map_in[player_in["y"]][player_in["x"]] = "M"

    # Check if player's backpack is full
    if player_in["capacity"] == sum_ores_in_backpack(player_in=player_in):
        print("You can't carry any more, so you can't go that way.\n"
            "You are exhausted.\n"
            "You place your portal stone here and zap back to town.")
        return True
    if player_in["turns"] == 0:
        print("You are exhausted.\n"
            "You place your portal stone here and zap back to town.")
        current_map_in[player_in["y"]][player_in["x"]] = "P"
        return True

    return False

# ------------------------- Menu Functions -------------------------


def main_menu(game_map_in, current_map_in, player_in) -> bool:
    '''Simulates the interaction of main menu.
    Return bool value specifies whether to exit program or not.'''
    global current_save_slot
    while True:
        show_main_menu()
        main_menu_choice: str = validate_input("Your choice? ",r"^[n|l|q]$")

        if main_menu_choice == "n":
            initialize_game(game_map_in=game_map_in, current_map_in=current_map_in,
                            player_in=player_in)
            save_game(save_slot_number=current_save_slot,
                      game_map_in=game_map_in, current_map_in=current_map_in, player_in=player_in)
            load_game(save_slot_number=current_save_slot,
                      game_map_in=game_map_in, current_map_in=current_map_in, player_in=player_in)
            return True
        if main_menu_choice == "l":
            save_slots_written_already: list[int] = find_written_slots(mode="load")
            if len(save_slots_written_already) == 0:
                print("There has not been a save slot written to. Please create a new save slot.")
                continue

            separator = "|"
            save_slots_written_already: list[str] = [str(n) for n in save_slots_written_already]
            regex = separator.join(save_slots_written_already)
            regex = create_regex(valid_char=regex)

            current_save_slot = int(validate_input("Your choice? ", regex))
            loaded_success: bool = load_game(save_slot_number=current_save_slot,
                                             game_map_in=game_map_in,
                                             current_map_in=current_map_in, player_in=player_in)
            if not loaded_success:
                continue
            return True
        if main_menu_choice == "q":
            return False


def shop_menu(player_in) -> None:
    '''Simulates the interaction of shop menu'''
    while True:
        if player_in["pickaxe_level"] <= len(pickaxe_prices):
            show_shop_menu(show_pickaxes=True, player_in=player_in)
            shop_menu_choice: str = validate_input("Your choice? ", r"^[p|b|l]$")
        else:
            show_shop_menu(show_pickaxes=False, player_in=player_in)
            shop_menu_choice: str = validate_input("Your choice? ", r"^[b|l]$")
        if shop_menu_choice == "p":
            pickaxe_price: int = pickaxe_prices[player_in["pickaxe_level"]-1]
            if player_in["GP"] >= pickaxe_price:
                player_in["GP"] -= pickaxe_price
                player_in["pickaxe_level"] += 1
                player_in["valid_minable_ores"] += minerals[player_in['pickaxe_level']-1][0].upper()
                print("Congratulations! "
                      f"You can now mine {minerals[player_in['pickaxe_level']-1]}!")
            else:
                print("You don't have enough GP!")
        elif shop_menu_choice == "b":
            price: int = player_in["capacity"] * 2
            if player_in["GP"] >= price:
                player_in["GP"] -= price
                player_in["capacity"] += 2
                print(f"Congratulations! You can now carry {player_in["capacity"]} items!\n")
            else:
                print("You don't have enough GP!")
        else:
            break


def mine_menu(player_in, game_map_in, current_map_in) -> bool:
    '''Simulates the interaction of mine menu.
    Return bool value specifies whether to return to main menu or not.'''
    while True:
        show_mine_menu(player_in=player_in)
        mine_menu_choice: str = validate_input("Action? ", r"^[w|a|s|d|m|i|p|q]$")
        if mine_menu_choice in "wasd":
            return_to_town_menu: bool = movement_in_mine(mine_menu_choice_input=mine_menu_choice,
                                                         player_in=player_in,
                                                         game_map_in=game_map_in,
                                                         current_map_in=current_map_in)
            if return_to_town_menu:
                new_day(player_in=player_in)
                return False
        elif mine_menu_choice == "m":
            draw_map(map_in=current_map_in, in_town=False)
        elif mine_menu_choice == "i":
            show_information(menu_type="mine", player_in=player_in)
        elif mine_menu_choice == "p":
            print("You place your portal stone here and zap back to town.")
            return False
        else:
            return True


def town_menu(player_in, game_map_in, current_map_in) -> None:
    '''Simulates the interaction of town menu'''
    # print(current_prices)
    while True:
        return_to_main_menu: bool = sell_ores(player_in=player_in)
        if return_to_main_menu:
            break

        show_town_menu(player_in=player_in)
        town_menu_choice: str = validate_input("Your choice? ", r"^[b|i|m|e|v|q]$")

        if town_menu_choice == "b":
            shop_menu(player_in=player_in)
        elif town_menu_choice == "i":
            show_information(menu_type="town", player_in=player_in)
        elif town_menu_choice == "m":
            draw_map(map_in=current_map_in, in_town=True)
        elif town_menu_choice == "e":
            return_to_main_menu: bool = mine_menu(player_in=player_in,
                                                  game_map_in=game_map_in,
                                                  current_map_in=current_map_in)
            if return_to_main_menu:
                break
        elif town_menu_choice == "v":
            save_game(save_slot_number=current_save_slot,
                  game_map_in=game_map_in, current_map_in=current_map_in, player_in=player_in)
        else:
            break


def main():
    '''Main game'''
    #--------------------------- Creating the save slot folders ---------------------------
    # Ensures they exist in working dir.
    # Source: https://www.geeksforgeeks.org/python/create-a-directory-in-python/

    for i in range(1, SAVE_SLOT_QUANTITY+1):
        full_dir_path: str = get_save_slot_dir(number=i)
        try: # The exceptions are only for debugging
            os.mkdir(full_dir_path)
            # print(f"Directory '{full_dir_path}' created successfully.")
        except FileExistsError:
            #print(f"Directory '{full_dir_path}' already exists.")
            pass
        except PermissionError:
            #print(f"Permission denied: Unable to create '{full_dir_path}'.")
            assert False, f"Permission denied: Unable to create '{full_dir_path}'."
        except Exception as e:
            assert False, f"An error occurred while attempting creating {full_dir_path}: {e}"

    #--------------------------- MAIN GAME ---------------------------
    game_state: str = 'main'
    print("---------------- Welcome to Sundrop Caves! ----------------")
    print("You spent all your money to get the deed to a mine, a small")
    print("  backpack, a simple pickaxe and a magical portal stone.")
    print()
    print("How quickly can you get the 1000 GP you need to retire")
    print("  and live happily ever after?")
    print("-----------------------------------------------------------")

    while True: # MAIN LOOP
        continue_from_main: bool = main_menu(game_map_in=game_map,
                                             current_map_in=current_map,
                                             player_in=player) # TRUE = CONTINUE
        if not continue_from_main:
            break

        town_menu(player_in=player, game_map_in=game_map, current_map_in=current_map)

    print("Thanks for playing")

if __name__=="__main__":
    main()
