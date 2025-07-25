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
fog = [] # (Update) :May NOT have to use this lol

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
current_prices: dict[str: int] = {}

pieces_per_node: dict[str: tuple[int]] = {}
pieces_per_node['copper'] = (1, 5)
pieces_per_node['silver'] = (1, 3)
pieces_per_node['gold'] = (1, 2)

current_save_slot: int = 1 # Needs to be globalised
SAVE_SLOT_QUANTITY: int = 5

WASD_TO_DIRECTION_AND_MOVE_VALUE: dict[str: dict[str: str]]= {
    "w": {"direction": "y", "move_value": -1},
    "a": {"direction": "x", "move_value": -1},
    "s": {"direction": "y", "move_value": 1},
    "d": {"direction": "x", "move_value": 1}}


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
    save_file_map = open(filename, "w")
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
    regex_out = f"^[{valid_char}]$"
    regex_out = r"{}".format(regex_out)
    return regex_out


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
                written_slots.append(i)
                save_slot_listing_text += f"\033[{written_colour}m{f"Slot {i}: HAS BEEN WRITTEN TO\n"}\033[00m"
            else:
                save_slot_listing_text += f"\033[{empty_colour}m{f"Slot {i}: EMPTY ; No files in save folder\n"}\033[00m"

    if len(written_slots) > 0:
        print(save_slot_listing_text) # lists whether a save slot is empty or has data already written to it.
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

    map_file = open(filename, 'r')
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


# $$$$$ NOTE FOR NOW NOT USED
# MY DEFINITION: UPDATES current_map, using player pos, to reveal fog of war
# def clear_fog(fog, player: dict): # Kinda broken
#     '''This function clears the fog of war at the 3x3 square around the player'''

#     for i in range(-1, 2): # MAY NEED TO CHANGE
#         row_n = player["y"] + i
#         for j in range(-1,2):
#             col_n = player["x"] + j
#             if 0 <= row_n <= (MAP_HEIGHT - 1) and 0 <= col_n <= (MAP_WIDTH-1):
#                 current_map[row_n][col_n] = game_map[row_n][col_n]
#     current_map[player["y"]][player["x"]] = "M"

#     return


def initialize_game() -> None: # default values
    # game_map: list = game_map, fog = [], \
    #                 player: dict = player
    '''Initiliases game_map, current_map and player information'''
    global current_save_slot

    current_save_slot = choose_new_save_slot()
    name: str = validate_input("Greetings, miner! What is your name? ", r"^.+$")

    # initialise map
    try:
        load_map("level1.txt", game_map)
    except FileNotFoundError:
        print("FileNotFoundError; Please check that the level map exists again.")

    # Create current map WITH fog TODO Create a function that does this
    for _ in range(MAP_HEIGHT):
        row: list[str] = ["?" for _ in range(MAP_WIDTH)]
        current_map.append(row)
    current_map[0][0] = "M"

    # TODO: initialize fog (may not be needed)

    # initialize player
    player['name'] = name
    player['x'] = 0
    player['y'] = 0
    player['copper'] = 0
    player['silver'] = 0
    player['gold'] = 0
    player['GP'] = 0
    player['day'] = 1 # changed from 0
    player['steps'] = 0
    player['turns'] = TURNS_PER_DAY

    # NEW BELOW
    player['capacity'] = 10
    player["pickaxe_level"] = 1
    player["valid_minable_ores"] = "C" # uses first letters of minerals to check if player can mine

    # TODO clear_fog(fog, player) (may not be needed)

    save_game()
    print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")


def draw_map(game_map, fog, player, in_town: bool) -> None:
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
            if in_town and game_map[i][j] == "M": # Special case 2
                row_text += "P"
                continue

            row_text += game_map[i][j]
        output_text += f"|{row_text}|\n"
    output_text += f"+{"-"*MAP_WIDTH}+"

    print(output_text)


def draw_view(game_map, fog, player) -> None: # game_map, fog, player
    '''This function draws the 3x3 viewport'''
    print(f"DAY {player['day']}")
    x: int = player["x"]
    y: int = player["y"]

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
                view_to_print += current_map[row_n][col_n]
            else: # Draws wall of mine
                view_to_print += "#"
        view_to_print += "|\n"
    view_to_print += "+---+"
    print(view_to_print)


def get_save_slot_dir(number: int) -> str:
    '''Returns save slot directory name based on slot number.'''
    return f"saves/save_slot_{number}"


def save_game(save_slot_number: int = current_save_slot) -> None: # default values
    # game_map: list = game_map, fog = [], player: dict = player,\
    '''This function saves the game'''
    directory_name: str = get_save_slot_dir(number=save_slot_number)

    # Saving game map
    save_list_to_txt(f"{directory_name}/save_{save_slot_number}_map.txt", game_map)

    # Saving current map
    save_list_to_txt(f"{directory_name}/save_{save_slot_number}_current_map.txt", current_map)

    # save fog TODO

    # Saving player info
    save_file_player = open(f"{directory_name}/save_{save_slot_number}_player.txt", "w")
    text_to_write: str = ""
    for key, value in player.items():
        if isinstance(value, (int, float, str)):
            text_to_write += f"{key},{value}\n"
    text_to_write = text_to_write[:len(text_to_write)-1] # Removes extra \n
    save_file_player.write(text_to_write)
    save_file_player.close()

    print(f"Saved to save slot {save_slot_number}")


def load_game(save_slot_number: int = current_save_slot) -> bool: # default values
    # game_map: list = game_map, fog = [], player: dict = player
    '''This function loads the game.'''
    directory_name: str = get_save_slot_dir(number=save_slot_number)

    try:
        # load map
        load_map(f"{directory_name}/save_{save_slot_number}_map.txt", game_map)
        load_map(f"{directory_name}/save_{save_slot_number}_current_map.txt", current_map)
        # print(f"game_map: {game_map}")

        # TODO load fog

        # load player
        player.clear()
        save_file_player = open(f"{directory_name}/save_{save_slot_number}_player.txt", "r")
        data: list[str] = save_file_player.read().split("\n")

        for datum in data:
            datum: list[str] = datum.split(",")
            try: # typecasting strings into floats and integers
                if "." in datum[1]:
                    datum[1] = float(datum[1])
                else:
                    datum[1] = int(datum[1])
                player[datum[0]] = datum[1]
            except ValueError: # for strings
                player[datum[0]] = datum[1]
        save_file_player.close()

        # Sets the prices for that day.
        set_prices()

        return True
    except FileNotFoundError:
        print("There is not a saved game. Please start a new game.")
        return False


# ------------------------- Functions that show INFORMATION -------------------------


def show_information(menu_type: str) -> None: # player argument
    '''This function shows the information for the player.'''
    print("\n----- Player Information -----")
    print(f"Name: {player["name"]}")
    assert menu_type in ["town", "mine"], f"menu_type = {menu_type} is wrong. check again"

    if menu_type == "town":
        print(f"Portal position: {(player["x"], player["y"])}")
    else:
        print(f"Current position: {(player["x"], player["y"])}")
    print(f"Pickaxe level: {player['pickaxe_level']} ({minerals[player['pickaxe_level']-1]})")
    if menu_type == "mine":
        minerals.reverse()
        for mineral in minerals:
            print(f"{mineral.capitalize()}: {player[mineral]}")

    print("------------------------------")
    print(f"Load: {sum_ores_in_backpack()} / {player["capacity"]}")
    print("------------------------------")
    print(f"GP: {player["GP"]}")
    print(f"Steps taken: {player["steps"]}")
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


def show_town_menu() -> None:
    '''Shows town menu'''
    print()
    print(f"DAY {player['day']}")
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")


def show_shop_menu(show_pickaxes: bool) -> None: # gp: int parameter
    '''Shows shop menu'''
    print("\n----------------------- Shop Menu -------------------------")
    if show_pickaxes:
        pickaxe_price: int = pickaxe_prices[player["pickaxe_level"]-1]
        print(f"(P)ickaxe upgrade to Level {player['pickaxe_level']+1} "
              f"to mine {minerals[player['pickaxe_level']]} ore for {pickaxe_price} GP")

    backpack_upgrade_price: int = player["capacity"] * 2
    print(f"(B)ackpack upgrade to carry {player["capacity"]+2} items "
          f"for {backpack_upgrade_price} GP")
    print("(L)eave shop")
    print("-----------------------------------------------------------")
    print(f"GP: {player["GP"]}")
    print("-----------------------------------------------------------")


def show_mine_menu() -> None:
    '''Shows mine menu'''
    print("---------------------------------------------------")
    print(f"{f"DAY {player['day']}":^50}")
    print("---------------------------------------------------")
    draw_view(game_map=current_map, fog=[], player=player)
    print(f"Turns left: {player['turns']} {" "*4} Load: "
          f"{sum_ores_in_backpack()} / {player["capacity"]} "
          f"{" "*4} Steps: {player['steps']}")
    print("(WASD) to move")
    print("(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu")


def show_game_won() -> None:
    '''Shows game win information'''
    print("-------------------------------------------------------------")
    print(f"Woo-hoo! Well done, Cher, you have {player["GP"]} GP!")
    print("You now have enough to retire and play video games every day.")
    print(f"And it only took you {player["day"]} days and "
          f"{player["steps"]} steps! You win!")
    print("-------------------------------------------------------------")


# ------------------------- Various functions that are used in Menus -------------------------


def new_day() -> None:
    '''When a new day passes, does the following.'''
    player["turns"] = TURNS_PER_DAY
    player["day"] += 1
    set_prices()


def sum_ores_in_backpack() -> int:
    '''Returns the sum of the quantity of minerals in backpack.'''
    return sum(player[mineral] for mineral in minerals)


def set_prices() -> None:
    '''Sets the prices for minerals. To be called at the start of a new day.'''
    current_prices.clear()
    for mineral in minerals:
        current_prices[mineral] = randint(prices[mineral][0], prices[mineral][1])


def sell_ores() -> bool:
    '''Sells ores. Checks if player has won the game.'''
    have_sold_stuff: bool = False
    for mineral in minerals:
        if player[mineral] > 0:
            GP_sold: int = player[mineral] * current_prices[mineral]
            print(f"You sell {player[mineral]} {mineral} ore for {GP_sold} GP.")
            player["GP"] += GP_sold
            player[mineral] = 0
            have_sold_stuff = True
    if have_sold_stuff:
        print(f"You now have {player["GP"]} GP!")
    if player["GP"] >= WIN_GP:
        show_game_won()
        return True
    return False


def is_ore_minable(ore_found_input: str) -> bool:
    '''Checks if the ore found can be mined depending on pickaxe level.'''
    if ore_found_input in player["valid_minable_ores"]:
        print("You can mine this!")
        return True
    print(f"Your pickaxe level ({player['pickaxe_level']}) is "
        f"too low, so you cannot mine {mineral_names[ore_found_input]}.")
    return False


def valid_move_checker(direction: str, move_value: int) -> bool:
    '''Checks if a move of WASD is valid.
    direction = "x" or "y"
    move_value = -1 or 1'''
    # Input checks
    if direction not in ["x", "y"]:
        raise ValueError(f"{direction} is an invalid value for direction")
    if move_value not in [1,-1]:
        raise ValueError(f"{move_value} is an invalid value for move_value")

    player["turns"] -= 1
    player["steps"] += 1

    # Determines new hypothetical position and square
    position_to_check: dict[str: int] = {"x": player["x"], "y": player["y"]}
    position_to_check[direction] += move_value
    # print(f"{position_to_check["x"]}, {position_to_check['y']}")

    # Checks if hypothetical position is within map boundaries
    if not is_within(height=MAP_HEIGHT, width=MAP_WIDTH,
                     x=position_to_check["x"], y=position_to_check["y"]):
        print("You can't go that way.")
        return False

    # Determines new hypothetical square
    square_to_check: str = current_map[position_to_check["y"]][position_to_check["x"]]

    # Checks if player's backpack is full and if the square to be stepped on is a mineral
    is_player_backpack_full: bool = sum_ores_in_backpack() == player["capacity"]
    is_next_square_a_mineral: bool = square_to_check in list(key for key in mineral_names)
    if is_player_backpack_full and is_next_square_a_mineral:
        print("You can't carry any more, so you can't go that way.")
        return False

    if square_to_check in mineral_names:
        return is_ore_minable(ore_found_input=square_to_check)

    return True


def process_ore_into_backpack(ore_found_input: str) -> None:
    '''Adds the pieces of ore found into the backpack depending on backpack capacity.'''
    remaining_space_in_backpack: int = player["capacity"] - sum_ores_in_backpack()
    mineral_name: str = mineral_names[ore_found_input]
    pieces_found: int = randint(pieces_per_node[mineral_name][0], pieces_per_node[mineral_name][1])

    if pieces_found <= remaining_space_in_backpack:
        print(f"You mined {pieces_found} piece(s) of {mineral_name}.")
        player[mineral_names[ore_found_input]] += pieces_found
    else:
        print(f"You mined {pieces_found} piece(s) of {mineral_name}.")
        print(f"...but you can only carry {remaining_space_in_backpack} more piece(s)!")
        player[mineral_names[ore_found_input]] += remaining_space_in_backpack


def movement_in_mine(mine_menu_choice_input: str) -> bool:
    '''Simulates movement in the mine (WASD input in Mine Menu)'''
    direction: str = WASD_TO_DIRECTION_AND_MOVE_VALUE[mine_menu_choice_input]["direction"]
    move_value: int = WASD_TO_DIRECTION_AND_MOVE_VALUE[mine_menu_choice_input]["move_value"]
    if valid_move_checker(direction=direction,move_value=move_value):
        # print("YAY you can move!")
        # Restore square to be stepped away (was previously covered by player avatar)
        current_map[player["y"]][player["x"]] = game_map[player["y"]][player["x"]]

        player[direction] += move_value # Update player position

        # Update positions within 3x3 square from player;
        # update current_map using game_map (clears fog)
        positions_to_update: list[dict[str: int]] = determine_square_grid_in_list(x=player["x"],
                                                            y=player["y"],
                                                            list_height=MAP_HEIGHT,
                                                            list_width=MAP_WIDTH)[0]
        for position in positions_to_update:
            y = position["y"]
            x = position["x"]
            current_map[y][x] = game_map[y][x]

        square_stepped: str = current_map[player["y"]][player["x"]]

        if square_stepped in mineral_names: # if an ore was stepped on
            ore_found: str = current_map[player["y"]][player["x"]]
            # print(f"Ore found: {ore_found}")
            process_ore_into_backpack(ore_found_input=ore_found)
            game_map[player["y"]][player["x"]] = " " # Remove ore vein
        elif square_stepped == "T":
            # If you step on the
            # 'T' square at (0, 0), you will return to town
            new_day()
            print("You returned to town.")
            return True

        current_map[player["y"]][player["x"]] = "M"

    # Check if player's backpack is full
    if player["capacity"] == sum_ores_in_backpack():
        print("You can't carry any more, so you can't go that way.\n"
            "You are exhausted.\n"
            "You place your portal stone here and zap back to town.")
        new_day()
        return True
    if player["turns"] == 0:
        new_day()
        print("You are exhausted.\n"
            "You place your portal stone here and zap back to town.")
        current_map[player["y"]][player["x"]] = "P"
        return True

    return False

# ------------------------- Menu Functions -------------------------


def main_menu() -> bool: # Return value specifies whether to break out of MAIN LOOP
    '''Simulates the interaction of main menu'''
    while True:
        show_main_menu()
        main_menu_choice: str = validate_input("Your choice? ",r"^[n|l|q]$")

        if main_menu_choice == "n":
            initialize_game()
            load_game()
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

            save_slot_choice: int = int(validate_input("Your choice? ", regex))
            loaded_success: bool = load_game(save_slot_number=save_slot_choice)
            if not loaded_success:
                continue
            return True
        if main_menu_choice == "q":
            return False


def shop_menu() -> None:
    '''Simulates the interaction of shop menu'''
    while True:
        if player["pickaxe_level"] <= len(pickaxe_prices):
            show_shop_menu(show_pickaxes=True)
            shop_menu_choice: str = validate_input("Your choice? ", r"^[p|b|l]$")
        else:
            show_shop_menu(show_pickaxes=False)
            shop_menu_choice: str = validate_input("Your choice? ", r"^[b|l]$")
        if shop_menu_choice == "p":
            pickaxe_price: int = pickaxe_prices[player["pickaxe_level"]-1]
            if player["GP"] >= pickaxe_price:
                player["GP"] -= pickaxe_price
                player["pickaxe_level"] += 1
                player["valid_minable_ores"] += minerals[player['pickaxe_level']-1][0].upper()
                print(f"Congratulations! You can now mine {minerals[player['pickaxe_level']-1]}!")
        elif shop_menu_choice == "b":
            price: int = player["capacity"] * 2
            if player["GP"] >= price:
                player["GP"] -= price
                player["capacity"] += 2
                print(f"Congratulations! You can now carry {player["capacity"]} items!\n")
            else:
                print("You don't have enough GP!")
        else:
            break


def mine_menu() -> bool:
    '''Simulates the interaction of mine menu'''
    while True:
        show_mine_menu()
        mine_menu_choice: str = validate_input("Action? ", r"^[w|a|s|d|m|i|p|q]$")
        if mine_menu_choice in "wasd":
            return_to_town_menu: bool = movement_in_mine(mine_menu_choice_input=mine_menu_choice)
            if return_to_town_menu:
                return False
        elif mine_menu_choice == "m":
            draw_map(game_map=current_map, fog=[], player=player, in_town=False)
        elif mine_menu_choice == "i":
            show_information("mine")
        elif mine_menu_choice == "p":
            print("You place your portal stone here and zap back to town.")
            return False
        else:
            return True


def town_menu() -> None:
    '''Simulates the interaction of town menu'''
    while True:
        return_to_main_menu: bool = sell_ores() # True = return to main menu
        if return_to_main_menu:
            break

        show_town_menu()
        town_menu_choice: str = validate_input("Your choice? ", r"^[b|i|m|e|v|q]$")

        if town_menu_choice == "b":
            shop_menu()
        elif town_menu_choice == "i":
            show_information("town")
        elif town_menu_choice == "m":
            draw_map(game_map=current_map, fog=[], player=player, in_town=True)
        elif town_menu_choice == "e":
            return_to_main_menu: bool = mine_menu()
            if return_to_main_menu: # TRUE = return to main menu
                break
        elif town_menu_choice == "v":
            save_game()
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
        continue_from_main: bool = main_menu() # TRUE = CONTINUE
        if not continue_from_main:
            break

        town_menu()

    print("Thanks for playing")

if __name__=="__main__":
    main()
