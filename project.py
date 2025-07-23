# TODO The program should have sufficient comments,
# which includes your name, class, date, overall
# description of what the program does, as well
# as the description of the functions.

from random import randint
import os
import re

player = {}
game_map = []
fog = [] # May have to use this lol

current_map = []

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_prices = [50, 150]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

current_prices = {} # NEW

current_save_slot = 1 # Needs to be globalised
SAVE_SLOT_QUANTITY = 5

WASD_TO_DIRECTION_AND_MOVE_VALUE = {"w": {"direction": "y", "move_value": -1},
                                    "a": {"direction": "x", "move_value": -1},
                                    "s": {"direction": "y", "move_value": 1},
                                    "d": {"direction": "x", "move_value": 1}}


# ------------------------- GENERAL Functions -------------------------


# Assumes that input will be a SINGLE LETTER
def validate_input(message: str, regex: str) -> str:
    '''Uses a regular expression to validate input. Takes in a prompt and a regex.'''
    # need to typecast in main code when working outside of strings
    while True:
        user_input = input(message).lower()
        if re.match(regex, user_input):
            return user_input
        elif user_input == "":
            print("Please enter a valid input instead of nothing.")
        else:
            print(f"{user_input} is invalid. Please enter a valid input.")


def save_list_to_txt(filename: str, input_list: list) -> None:
    '''Saves a list into a text file.'''
    save_file_map = open(filename, "w")
    text_to_write = ""
    for row in input_list:
        for element in row:
            text_to_write += element
        text_to_write += "\n"
    text_to_write = text_to_write[:len(text_to_write)-1]
    save_file_map.write(text_to_write)
    save_file_map.close()


def determine_square_grid_in_list(x: int, y: int,
                                  list_height: int,
                                  list_width: int) -> list[dict[int, int]]: # two_d_list_input: list
    '''Returns a list of dicts of positions, satisfying the following:
    The positions are within a square of side 3 as the (x,y) the centre.
    I.e. positions that are within a Manhattan Distance of 2 units, exclduing (x,y)'''
    valid_positions = []
    for i in range(-1, 2):
        row_n = y + i
        for j in range(-1,2):
            col_n = x + j

            # Excludes the centre of the square
            is_not_centre = not(col_n == x and row_n == y)
            # Checks if position found is within list's boundaries
            is_within = 0 <= row_n <= (list_height-1) and 0 <= col_n <= (list_width-1)

            if is_within and is_not_centre:
                valid_positions.append({"x": col_n, "y": row_n})
    return valid_positions


# ------------------------- Initialise-, Load-, Save-related Functions -------------------------


def checking_save_slots(mode: str) -> tuple[str, list]:
    '''
    Checks all of the save slot folders to see if they are empty or not
    Takes in a mode for different print messages.
    Returns
    1. the text that lists whether a save slot is empty or has data already written to it
    2. a list of save slots that has data already written to it
    '''
    assert mode in ["save", "load"], f"{mode} is invalid. Valid: {["save", "load"]}. Please check again."

    written_colour, empty_colour = 91, 92
    if mode == "save":
        save_slot_listing_text = "Select a save slot to save to.\n"
    elif mode == "load":
        save_slot_listing_text = "Select a save slot to load from.\n"
        written_colour = 92
        empty_colour = 91

    save_slots_written_already = []
    for i in range(1,SAVE_SLOT_QUANTITY+1):
        try:
            directory = os.listdir(f"saves/save_slot_{i}")
        except FileNotFoundError:
            assert False, f"\033[91m{f"Slot {i}: EMPTY ; FileNotFoundError; Please check that this folder has been created."}\033[00m"
        else:
            if len(directory) != 0:
                save_slots_written_already.append(i)
                save_slot_listing_text += f"\033[{written_colour}m{f"Slot {i}: HAS BEEN WRITTEN TO\n"}\033[00m"
            else:
                save_slot_listing_text += f"\033[{empty_colour}m{f"Slot {i}: EMPTY ; No files in save folder\n"}\033[00m"

    return save_slot_listing_text, save_slots_written_already


def choose_new_save_slot() -> int:
    '''Allows choosing of save slot to begin a NEW game.'''

    # Checking every safe slot directory
    save_slot_listing_text, save_slots_written_already = checking_save_slots(mode="save")

    # Creating regex for input validation based on number of save slots.
    separator = "|"
    regex = separator.join([str(i) for i in list(range(1,SAVE_SLOT_QUANTITY))]) # HARD CODED !!!!
    regex = f"^[{regex}]$"
    regex = r"{}".format(regex)

    print(save_slot_listing_text)

    # Asking user for desired save slot choice
    while True:
        save_slot_choice = int(validate_input("Your choice? ", regex))
        if save_slot_choice in save_slots_written_already:
            confirmation_choice = validate_input(f"Are you sure? This will overwrite save "
                                                 f"slot {save_slot_choice}. "
                                                 "Your choice (y/n)? ", r"^[y|n]$")
            if confirmation_choice == "n":
                print(f"You chose not to overwrite save slot {save_slot_choice}")
                continue
        break

    return save_slot_choice


def load_map(filename: str, map_struct: list) -> None:
    # map_struct is
    # probably saying which variable to save to
    # variable to edit
    '''
    Loads a map structure (a nested list) from a file.
    It also updates MAP_WIDTH and MAP_HEIGHT'''

    map_file = open(filename, 'r')
    global MAP_WIDTH
    global MAP_HEIGHT

    map_struct.clear() # not sure what this is for

    lines = map_file.read().split("\n")
    for line in lines:
        line = list(line)
        map_struct.append(line)

    MAP_WIDTH = len(map_struct[0])
    MAP_HEIGHT = len(map_struct)

    map_file.close()


# MY DEFINITION: UPDATES current_map, using player pos, to reveal fog of war
def clear_fog(fog, player: dict):
    '''This function clears the fog of war at the 3x3 square around the player'''

    for i in range(-1, 2): # MAY NEED TO CHANGE
        row_n = player["y"] + i
        for j in range(-1,2):
            col_n = player["x"] + j
            if 0 <= row_n <= (MAP_HEIGHT - 1) and 0 <= col_n <= (MAP_WIDTH-1):
                current_map[row_n][col_n] = game_map[row_n][col_n]
    current_map[player["y"]][player["x"]] = "M"

    return


def initialize_game() -> None: # default values
    # game_map: list = game_map, fog = [], \
    #                 player: dict = player
    '''Initiliases map, fog and player information'''
    global current_save_slot

    current_save_slot = choose_new_save_slot()
    name = validate_input("Greetings, miner! What is your name? ", r"^.+$")

    # initialise map
    try:
        load_map("level1.txt", game_map)
    except FileNotFoundError:
        print("FileNotFoundError; Please check that the level map exists again")

    # Create current map with fog
    for _ in range(MAP_HEIGHT):
        row = ["?" for _ in range(MAP_WIDTH)]
        current_map.append(row)
    current_map[0][0] = "M"

    # TODO: initialize fog

    # TODO: initialize player
    #   You will probably add other entries into the player dictionary
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

    # TODO clear_fog(fog, player)
    clear_fog(fog, player)
    draw_map(game_map=game_map, fog=[], player=player)
    draw_map(game_map=current_map, fog=[], player=player)

    save_game()
    print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")


def draw_map(game_map, fog, player):
    '''This function draws the entire map, covered by the fog'''

    print(f"\n+{"-"*MAP_WIDTH}+")
    for row in game_map: # Can generalise this into a UDF
        row_text = ""
        for cell in row:
            row_text += cell
        print(f"|{row_text}|")
    print(f"+{"-"*MAP_WIDTH}+")
    return


def draw_view(game_map, fog, player):
    '''This function draws the 3x3 viewport'''
    print("VIEW PORT")
    print(f"DAY {player['day']}")
    # print("+---+")  # MAY NEED TO CHANGE
    # for row in fog:
    #     row_text = ""
    #     for cell in row:
    #         row_text += cell
    #     print(f"|{row_text}|")
    # print("+---+")
    return


def save_game(save_slot_number: int = current_save_slot) -> None: # default values
    # game_map: list = game_map, fog = [], player: dict = player,\
    '''This function saves the game'''
    directory_name = f"saves/save_slot_{save_slot_number}"

    # save map list
    # Saving game map list
    save_list_to_txt(f"{directory_name}/save_{save_slot_number}_map.txt", game_map)

    # Saving current map
    save_list_to_txt(f"{directory_name}/save_{save_slot_number}_current_map.txt", current_map)

    # save fog TODO

    # save player
    # Saving str and int
    save_file_player = open(f"{directory_name}/save_{save_slot_number}_player.txt", "w")
    text_to_write = ""
    for key, value in player.items():
        if isinstance(value, (int, float, str)):
        # if type(player[key]) == str or type(player[key]) == int or type(player[key]) == float:
            text_to_write += f"{key},{value}\n"
    text_to_write = text_to_write[:len(text_to_write)-1]
    save_file_player.write(text_to_write)
    save_file_player.close()

    print(f"Saved to save slot {save_slot_number}")


def load_game(save_slot_number: int = current_save_slot) -> bool: # default values
    # game_map: list = game_map, fog = [], player: dict = player
    '''This function loads the game'''
    directory_name = f"saves/save_slot_{save_slot_number}"

    try:
        # load map
        load_map(f"{directory_name}/save_{save_slot_number}_map.txt", game_map)
        load_map(f"{directory_name}/save_{save_slot_number}_current_map.txt", current_map)
        # print(f"game_map: {game_map}")

        # TODO load fog

        # load player
        player.clear()
        save_file_player = open(f"{directory_name}/save_{save_slot_number}_player.txt", "r")
        data = save_file_player.read()
        data = data.split("\n")
        for datum in data: # extracting data from save slot
            datum = datum.split(",")
            try: # typecasting strings into floats and integers
                if "." in datum[1]:
                    datum[1] = float(datum[1])
                else:
                    datum[1] = int(datum[1])
                player[datum[0]] = datum[1]
            except ValueError: # for strings
                player[datum[0]] = datum[1]
        save_file_player.close()

        return True
    except FileNotFoundError:
        print("There is not a saved game. Please start a new game.")
        return False
    # print(player)


# ------------------------- Functions that show INFORMATION -------------------------


def show_information(menu_type: str) -> None: # player argument
    '''This function shows the information for the player'''
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
    backpack_upgrade_price = player["capacity"] * 2

    print("\n----------------------- Shop Menu -------------------------")
    if show_pickaxes:
        pickaxe_price = pickaxe_prices[player["pickaxe_level"]-1]
        print(f"(P)ickaxe upgrade to Level {player['pickaxe_level']+1} "
              f"to mine {minerals[player['pickaxe_level']]} ore for {pickaxe_price} GP")
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
          f"{player["steps"] * TURNS_PER_DAY + player["steps"]} steps! You win!")
    print("-------------------------------------------------------------")


# ------------------------- Various functions that are used in Menus -------------------------


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
    have_sold_stuff = False
    for mineral in minerals:
        if player[mineral] > 0:
            GP_sold = player[mineral] * current_prices[mineral]
            print(f"You sell {player[mineral]} {mineral} ore for {GP_sold} GP.")
            player["GP"] += GP_sold
            player[mineral] = 0
            have_sold_stuff = True
    if have_sold_stuff:
        print(f"You now have {player["GP"]} GP!")
    if player["GP"] >= WIN_GP:
        show_game_won()
        return True


def valid_move_checker(direction: str, move_value: int) -> bool:
    '''Checks if a move of WASD is valid.
    direction = "x" or "y"
    move_value = -1 or 1'''
    # TO consider:
    # https://pylint.readthedocs.io/en/latest/user_guide/messages/refactor/inconsistent-return-statements.html

    # Input checks
    if direction not in ["x", "y"]:
        raise AssertionError(f"{direction} is an invalid value for direction")
    if move_value not in [1,-1]:
        raise AssertionError(f"{move_value} is an invalid value for move_value")

    # Determines new hypothetical position and square
    position_to_check = {"x": player["x"], "y": player["y"]}
    position_to_check[direction] += move_value
    square_to_check = current_map[position_to_check["y"]][position_to_check["x"]]

    # Checks if player's backpack is full and if the square to be stepped on is a mineral
    is_player_backpack_full = sum_ores_in_backpack() == player["capacity"]
    is_next_square_a_mineral = square_to_check in list(key for key in mineral_names)
    if is_player_backpack_full and is_next_square_a_mineral:
        print("You can't carry any more, so you can't go that way.")
        return False

    # Checks if hypothetical position is within map boundaries
    is_x_valid = 0 <= position_to_check["x"] <= MAP_WIDTH - 1
    is_y_valid = 0 <= position_to_check["y"] <= MAP_HEIGHT - 1
    if is_x_valid and is_y_valid:
        return True
    print("You can't go that way.")
        # If you step on the ‘T’ square at (0, 0), you will return to town


def ore_found():
    '''Automates what happens if a player finds an ore.'''
    pass


# ------------------------- Menu Functions -------------------------


def main_menu() -> bool: # Return value specifies whether to break out of MAIN LOOP
    '''Simulates the interaction of main menu'''
    while True:
        show_main_menu()
        main_menu_choice = validate_input("Your choice? ",r"^[n|l|q]$")

        if main_menu_choice == "n":
            initialize_game()
            load_game()
            return True
            # break
        elif main_menu_choice == "l":
            save_slot_listing_text, save_slots_written_already = checking_save_slots(mode="load")
            if len(save_slots_written_already) == 0:
                print("There has not been a save slot written to. Please create a new save slot.")
                continue
            else:
                print(save_slot_listing_text)
                separator = "|"
                save_slots_written_already = [str(n) for n in save_slots_written_already]
                regex = separator.join(save_slots_written_already)
                regex = f"^[{regex}]$"
                regex = r"{}".format(regex)

                save_slot_choice = int(validate_input("Your choice? ", regex))
                loaded_success = load_game(save_slot_number=save_slot_choice)
                if not loaded_success:
                    continue
                return True
        elif main_menu_choice == "q":
            return False
            # break


def shop_menu() -> None:
    '''Simulates the interaction of shop menu'''
    while True:
        if player["pickaxe_level"] <= len(pickaxe_prices):
            show_shop_menu(show_pickaxes=True)
            shop_menu_choice = validate_input("Your choice? ", r"^[p|b|l]$")
        else:
            show_shop_menu(show_pickaxes=False)
            shop_menu_choice = validate_input("Your choice? ", r"^[b|l]$")
        if shop_menu_choice == "p":
            pickaxe_price = pickaxe_prices[player["pickaxe_level"]-1]
            if player["GP"] >= pickaxe_price:
                player["GP"] -= pickaxe_price
                player["pickaxe_level"] += 1
                player["valid_minable_ores"] += minerals[player['pickaxe_level']-1][0].upper()
                print(f"Congratulations! You can now mine {minerals[player['pickaxe_level']-1]}!")
        elif shop_menu_choice == "b":
            price = player["capacity"] * 2
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
        mine_menu_choice = validate_input("Action? ", r"^[w|a|s|d|m|i|p|q]$")
        if mine_menu_choice in "wasd":
            # TODO CREATE A NEW FUNCTION FOR SIMULATING MOVEMENT IN MINE
            direction = WASD_TO_DIRECTION_AND_MOVE_VALUE[mine_menu_choice]["direction"]
            move_value = WASD_TO_DIRECTION_AND_MOVE_VALUE[mine_menu_choice]["move_value"]
            if valid_move_checker(direction=direction,move_value=move_value):
                print("YAY you can move")
                # Restore square to be stepped away (was previously covered by player avatar)
                current_map[player["y"]][player["x"]] = game_map[player["y"]][player["x"]]

                # update current_map using game_map (clears fog)
                player[direction] += move_value # Update player position
                current_map[player["y"]][player["x"]] = game_map[player["y"]][player["x"]]

                positions_to_update = determine_square_grid_in_list(x=player["x"],
                                                                    y=player["y"],
                                                                    list_height=MAP_HEIGHT,
                                                                    list_width=MAP_WIDTH)
                for position in positions_to_update:
                    y = position["y"]
                    x = position["x"]
                    current_map[y][x] = game_map[y][x]

                if current_map[player["y"]][player["x"]] in mineral_names:
                    pass # (consider if new step is on an ore or not)
                # update view_port
            else:
                print("YOU CANNOT MOVE!")
        elif mine_menu_choice == "m":
            draw_map(game_map=current_map, fog=[], player=player)
        elif mine_menu_choice == "i":
            show_information("mine")
        elif mine_menu_choice == "p":
            print("You place your portal stone here and zap back to town.")
            break
        else:
            return True


def town_menu() -> bool:
    '''Simulates the interaction of town menu'''
    set_prices() # NEED TO RUN THIS WHENEVER A NEW DAY PASSES
    while True:
        return_to_main_menu = sell_ores() # True = return to main menu
        if return_to_main_menu:
            return True

        show_town_menu()
        town_menu_choice = validate_input("Your choice? ", r"^[b|i|m|e|v|q]$")

        if town_menu_choice == "b":
            shop_menu()
        elif town_menu_choice == "i":
            show_information("town")
        elif town_menu_choice == "m":
            draw_map(game_map=current_map, fog=[], player=player)
        elif town_menu_choice == "e":
            return_to_main_menu = mine_menu()
            if return_to_main_menu: # TRUE = return to main menu
                return True
        elif town_menu_choice == "v":
            save_game()
        else:
            return True


#--------------------------- Creating the save slot folders ---------------------------
# Ensures they exist in working dir.
# Source: https://www.geeksforgeeks.org/python/create-a-directory-in-python/
PRIMARY_DIRECTORY_NAME = "saves"

for j in range(1, SAVE_SLOT_QUANTITY+1):
    FULL_DIR_PATH = f"{PRIMARY_DIRECTORY_NAME}/save_slot_{j}"
    try: # The exceptions are only for debugging
        os.mkdir(FULL_DIR_PATH)
        # print(f"Directory '{FULL_DIR_PATH}' created successfully.")
    except FileExistsError:
        #print(f"Directory '{FULL_DIR_PATH}' already exists.")
        pass
    except PermissionError:
        #print(f"Permission denied: Unable to create '{FULL_DIR_PATH}'.")
        assert False, f"Permission denied: Unable to create '{FULL_DIR_PATH}'."
    except Exception as e:
        assert False, f"An error occurred while attempting creating {FULL_DIR_PATH}: {e}"


#--------------------------- MAIN GAME ---------------------------
game_state = 'main'
print("---------------- Welcome to Sundrop Caves! ----------------")
print("You spent all your money to get the deed to a mine, a small")
print("  backpack, a simple pickaxe and a magical portal stone.")
print()
print("How quickly can you get the 1000 GP you need to retire")
print("  and live happily ever after?")
print("-----------------------------------------------------------")

while True: # MAIN LOOP
    main_menu_continue_flag = main_menu() # TRUE = CONTINUE
    if not main_menu_continue_flag:
        break

    town_menu_continue_flag = town_menu() # TRUE = BREAK; FALSE = CONTINUE
    if not town_menu_continue_flag:
        break


print("Thanks for playing")
