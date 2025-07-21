from random import randint
import os
import re

player = {}
game_map = []
fog = []

MAP_WIDTH = 0
MAP_HEIGHT = 0

TURNS_PER_DAY = 20
WIN_GP = 500

minerals = ['copper', 'silver', 'gold']
mineral_names = {'C': 'copper', 'S': 'silver', 'G': 'gold'}
pickaxe_price = [50, 150]

prices = {}
prices['copper'] = (1, 3)
prices['silver'] = (5, 8)
prices['gold'] = (10, 18)

current_save_slot = 1
SAVE_SLOT_QUANTITY = 5


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


# This function loads a map structure (a nested list) from a file
# It also updates MAP_WIDTH and MAP_HEIGHT
def load_map(filename: str, map_struct: list = game_map) -> None:
    # idk what is map_struct; will asssign it some default value
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
    # return


# This function clears the fog of war at the 3x3 square around the player
def clear_fog(fog, player: dict):
    '''This function clears the fog of war at the 3x3 square around the player'''
    return


def checking_save_slots(mode: str) -> tuple[str, list]:
    '''
    Returns
    1. the text that lists whether a save slot is empty or has data already written to it
    2. a list of save slots that has data already written to it
    '''
    if mode == "save":
        save_slot_listing_text = "Select a save slot to save to.\n"
    elif mode == "load":
        save_slot_listing_text = "Select a save slot to load from.\n"
    
    save_slots_written_already = []
    for i in range(1,SAVE_SLOT_QUANTITY+1):
        try:
            dir = os.listdir(f"saves/save_slot_{i}")
        except FileNotFoundError:
            save_slot_listing_text += f"Slot {i}: EMPTY ; FileNotFoundError\n"
            continue
        else:
            if len(dir) != 0:
                save_slots_written_already.append(i)
                save_slot_listing_text += f"Slot {i}: HAS BEEN WRITTEN TO\n"
            else:
                save_slot_listing_text += f"Slot {i}: EMPTY ; No files in save folder\n"
    
    return save_slot_listing_text, save_slots_written_already


def choose_new_save_slot() -> int:
    '''Allows choosing of save slot to begin a NEW game.'''

    # Checking every safe slot directory
    save_slot_listing_text, save_slots_written_already = checking_save_slots(mode="save")
    
    # Creating regex for input validation based on number of save slots.
    separator = "|"
    regex = separator.join(list("12345")) # HARD CODED !!!!
    regex = f"^[{regex}]$"
    regex = r"{}".format(regex)

    print(save_slot_listing_text)

    # Asking user for desired save slot choice
    while True:
        save_slot_choice = int(validate_input("Your choice? ", regex))
        if save_slot_choice in save_slots_written_already:
            confirmation_choice = validate_input(f"Are you sure? This will overwrite save \
                                                 slot {save_slot_choice}. \
                                                 Your choice (y/n)? ", r"^[y|n]$")
            if confirmation_choice == "n":
                print(f"You chose not to overwrite save slot {save_slot_choice}")
                continue
        break

    return save_slot_choice


def initialize_game(game_map: list = game_map, fog = [], \
                    player: dict = player) -> None: # default values
    '''Initiliases map, fog and player information'''
    save_slot_choice = choose_new_save_slot()
    name = validate_input("Greetings, miner! What is your name? ", r"^.+$")

    # initialise map
    try:
        load_map("level1.txt")
    except FileNotFoundError:
        print("FileNotFoundError; Please check that the level map exists again")

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
    player['day'] = 0
    player['steps'] = 0
    player['turns'] = TURNS_PER_DAY

    # TODO
    # clear_fog(fog, player)

    save_game(save_slot_number=save_slot_choice)
    print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")


# This function draws the entire map, covered by the fog
def draw_map(game_map, fog, player):
    '''This function draws the entire map, covered by the fog'''
    return


# This function draws the 3x3 viewport
def draw_view(game_map, fog, player):
    '''This function draws the 3x3 viewport'''
    return


# This function shows the information for the player
def show_information(player):
    '''This function shows the information for the player'''
    return


# This function saves the game
def save_game(game_map: list = game_map, fog = [], player: dict = player,\
               save_slot_number: int = current_save_slot) -> None: # default values
    '''This function saves the game'''
    directory_name = f"saves/save_slot_{save_slot_number}"

    # save map
    # Saving map list
    save_file_map = open(f"{directory_name}/save_{save_slot_number}_map.txt", "w")
    text_to_write = ""
    for row in game_map:
        for element in row:
            text_to_write += element
        text_to_write += "\n"
    text_to_write = text_to_write[:len(text_to_write)-1]
    save_file_map.write(text_to_write)
    save_file_map.close()

    # save fog TODO

    # save player
    # Saving str and int
    save_file_player = open(f"{directory_name}/save_{save_slot_number}_player.txt", "w")
    text_to_write = ""
    for key in player.keys():
        if isinstance(player[key], (int, float, str)):
        # if type(player[key]) == str or type(player[key]) == int or type(player[key]) == float:
            text_to_write += f"{key},{player[key]}\n"
    text_to_write = text_to_write[:len(text_to_write)-1]
    save_file_player.write(text_to_write)
    save_file_player.close()

    print(f"Saved to save slot {save_slot_number}")
    # return


# This function loads the game
def load_game(game_map: list = game_map, fog = [], player: dict = player, \
              save_slot_number: int = current_save_slot) -> bool: # default values
    '''This function loads the game'''
    directory_name = f"saves/save_slot_{save_slot_number}"

    try:
        # load map
        load_map(f"{directory_name}/save_{save_slot_number}_map.txt")
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
    # TODO: Show Day
    print("----- Sundrop Town -----")
    print("(B)uy stuff")
    print("See Player (I)nformation")
    print("See Mine (M)ap")
    print("(E)nter mine")
    print("Sa(V)e game")
    print("(Q)uit to main menu")
    print("------------------------")


def show_shop_menu(gp: int) -> None:
    '''Shows shop menu'''
    print("----------------------- Shop Menu -------------------------")
    print("(P)ickaxe upgrade to Level {} to mine {} ore for {} GP")
    print("(B)ackpack upgrade to carry {} items for {} GP")
    print("(L)eave shop")
    print("-----------------------------------------------------------")
    print(f"GP: {gp}")
    print("-----------------------------------------------------------")


def main_menu() -> bool: # Return value specifies whether to break out of MAIN LOOP
    '''Main loop'''
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


def town_menu() -> bool:
    '''Simulates the interaction of town menu'''
    while True:
        show_town_menu()
        town_menu_choice = validate_input("Your choice? ", r"^[b|i|m|e|v|q]$")

        if town_menu_choice == "b": # (B)uy stuff
            # show_shop_menu() # Need to include input for current pickaxe level
            shop_menu_choice = validate_input("Your choice? ", r"^[p|b|l]$")
            # TODO purchasing mechanic
        elif town_menu_choice == "i":
            pass
        elif town_menu_choice == "m":
            pass
        elif town_menu_choice == "e":
            pass
        elif town_menu_choice == "v":
            save_game()
        else:
            return True


# Creating the save slot folders. Ensures they exist in working dir.
# Source: https://www.geeksforgeeks.org/python/create-a-directory-in-python/
PRIMARY_DIRECTORY_NAME = "saves"

for i in range(1,SAVE_SLOT_QUANTITY+1):
    FULL_DIR_PATH = f"{PRIMARY_DIRECTORY_NAME}/save_slot_{i}"
    try: # The exceptions are only for debugging
        os.mkdir(FULL_DIR_PATH)
        # print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        #print(f"Directory '{full_dir_path}' already exists.")
        pass
    except PermissionError:
        #print(f"Permission denied: Unable to create '{full_dir_path}'.")
        pass
    except Exception as e:
        print(f"An error occurred: {e}")


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
