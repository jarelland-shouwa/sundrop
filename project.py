from random import randint
import os
import re

player = {} # : {key: value, key, value}
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

# This function loads a map structure (a nested list) from a file
# It also updates MAP_WIDTH and MAP_HEIGHT
def load_map(filename: str, map_struct: list = game_map) -> None: # idk what is map_struct; will asssign it some default value
    '''
    Loads a map structure (a nested list) from a file.
    It also updates MAP_WIDTH and MAP_HEIGHT'''
    
    map_file = open(filename, 'r')
    global MAP_WIDTH
    global MAP_HEIGHT
    
    map_struct.clear() # not sure what this is for
    
    # TODO: Add your map loading code here DONE ✓
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

def initialize_game(game_map: list = game_map, fog = [], player: dict = player) -> None: # default values
    # Creating the save directory (ensures save directory exists in working directory)
    # Source: https://www.geeksforgeeks.org/python/create-a-directory-in-python/
    primary_directory_name = "saves"
    
    for i in range(1,SAVE_SLOT_QUANTITY+1):
        full_dir_path = f"{primary_directory_name}/save_slot_{i}"
        try: # The exceptions are only for debugging
            os.mkdir(full_dir_path)
            # print(f"Directory '{directory_name}' created successfully.")
        except FileExistsError:
            #print(f"Directory '{full_dir_path}' already exists.")
            pass
        except PermissionError:
            #print(f"Permission denied: Unable to create '{full_dir_path}'.")
            pass
        except Exception as e:
            print(f"An error occurred: {e}")
    
    # Choosing a save slot to save
    save_slot_listing_text = "Select a save slot to save to.\n"
    save_slots_written_already = []
    for i in range(1,SAVE_SLOT_QUANTITY+1):
        try:
            dir = os.listdir(f"saves/save_slot_{i}")
        except FileNotFoundError:
            save_slot_listing_text += f"Slot {i}: EMPTY ; FileNotFoundError\n"
            continue
        else:
            if len(dir) != 0:
                save_slot_listing_text += f"Slot {i}: HAS BEEN WRITTEN TO\n"
                save_slots_written_already.append(i)
            else:
                save_slot_listing_text += f"Slot {i}: EMPTY ; No files in save folder\n"
    
    separator = "|"
    file_quantity_in_all_save_dirs = "12345" # HARD CODED !!!!
    regex = separator.join(list(file_quantity_in_all_save_dirs))
    regex = f"^[{regex}]$"
    regex = r"{}".format(regex)
    
    print(save_slot_listing_text)
    while True:
        save_slot_choice = int(validate_input("Your choice? ", regex))
        if save_slot_choice in save_slots_written_already:
            confirmation_choice = validate_input(f"Are you sure? This will overwrite save slot {save_slot_choice}. Your choice (y/n)? ", r"^[y|n]$")
            if confirmation_choice == "n":
                print(f"You chose not to overwrite save slot {save_slot_choice}")
                continue
        break

    name = validate_input("Greetings, miner! What is your name? ", r"^.+$")

    # initialize map
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

    # clear_fog(fog, player) TODO

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
def save_game(game_map: list = game_map, fog = [], player: dict = player, save_slot_number: int = current_save_slot) -> None: # default values
    '''This function saves the game'''
    primary_directory_name = f"saves/save_slot_{save_slot_number}"

    # save map
    # Saving map list
    save_file_map = open(f"{primary_directory_name}/save_{save_slot_number}_map.txt", "w")
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
    save_file_player = open(f"{primary_directory_name}/save_{save_slot_number}_player.txt", "w")
    text_to_write = ""
    for key in player.keys():
        if type(player[key]) == str or type(player[key]) == int:
            text_to_write += f"{key},{player[key]}\n"
    text_to_write = text_to_write[:len(text_to_write)-1]
    save_file_player.write(text_to_write)
    save_file_player.close()

    print(f"Saved to save slot {save_slot_number}")
    # return
        
# This function loads the game
def load_game(game_map: list = game_map, fog = [], player: dict = player, save_slot_number: int = current_save_slot) -> bool: # default values
    '''This function loads the game'''
    primary_directory_name = f"saves/save_slot_{save_slot_number}"

    try:
        # load map
        load_map(f"{primary_directory_name}/save_{save_slot_number}_map.txt")
        # print(f"game_map: {game_map}")

        # load fog

        # load player
        player.clear()
        save_file_player = open(f"{primary_directory_name}/save_{save_slot_number}_player.txt", "r")
        data = save_file_player.read()
        data = data.split("\n")
        for datum in data:
            datum = datum.split(",")
            try:
                if "." in datum[1]:
                    datum[1] = float(datum[1])
                else:
                    datum[1] = int(datum[1])
                player[datum[0]] = datum[1]
            except ValueError:
                player[datum[0]] = datum[1]
        save_file_player.close()
        return True
    except FileNotFoundError:
        print("There is not a saved game. Please start a new game.")
        return False
    # print(player)
    # return

def show_main_menu() -> None:
    print()
    print("--- Main Menu ----")
    print("(N)ew game")
    print("(L)oad saved game")
    # print("(H)igh scores")
    print("(Q)uit")
    print("------------------")

def show_town_menu() ->None:
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


def show_shop_menu(GP: int) -> None:
    print("----------------------- Shop Menu -------------------------")
    print("(P)ickaxe upgrade to Level {} to mine {} ore for {} GP")
    print("(B)ackpack upgrade to carry {} items for {} GP")
    print("(L)eave shop")
    print("-----------------------------------------------------------")
    print(f"GP: {GP}")
    print("-----------------------------------------------------------")


def validate_input(message: str, regex: str) -> str: # need to typecast in main code when working outside of strings
    while True:
        user_input = input(message).lower()
        if re.match(regex, user_input):
            return user_input
        elif user_input == "":
            print(f"Please enter a valid input instead of nothing.")
        else:
            print(f"{user_input} is invalid. Please enter a valid input.")


#--------------------------- MAIN GAME ---------------------------
game_state = 'main'
print("---------------- Welcome to Sundrop Caves! ----------------")
print("You spent all your money to get the deed to a mine, a small")
print("  backpack, a simple pickaxe and a magical portal stone.")
print()
print("How quickly can you get the 1000 GP you need to retire")
print("  and live happily ever after?")
print("-----------------------------------------------------------")

# The game
while True:
    show_main_menu()
    main_menu_choice = validate_input("Your choice? ",r"^[n|l|q]$")

    if main_menu_choice == "n":
        initialize_game()
        load_game()
    elif main_menu_choice == "l":
        save_slot_listing_text = "Select a save slot to load from.\n"
        file_quantity_in_all_save_dirs = ""
        for i in range(1,SAVE_SLOT_QUANTITY+1):
            try:
                dir = os.listdir(f"saves/save_slot_{i}")
            except FileNotFoundError:
                save_slot_listing_text += f"Slot {i}: EMPTY ; FileNotFoundError\n"
                continue
            else:
                if len(dir) != 0:
                    file_quantity_in_all_save_dirs += str(i)
                    save_slot_listing_text += f"Slot {i}: HAS BEEN WRITTEN TO\n"
                else:
                    save_slot_listing_text += f"Slot {i}: EMPTY ; No files in save folder\n"
        if len(file_quantity_in_all_save_dirs) == 0:
            print("There has not been a save slot written to. Please create a new save slot.")
            continue
        else:
            print(save_slot_listing_text)
            separator = "|"
            regex = separator.join(list(file_quantity_in_all_save_dirs))
            regex = f"^[{regex}]$"
            regex = r"{}".format(regex)

            save_slot_choice = int(validate_input("Your choice? ", regex))
            loaded_success = load_game(save_slot_number=save_slot_choice)
            if not loaded_success:
                continue
    elif main_menu_choice == "q":
        break
    
    show_town_menu()
    town_menu_choice = validate_input("Your choice? ", r"^[b|i|m|e|v|q]$")
    
    # DON'T TOUCH BELOW YET (DEAL WITH SAVING MECHANIC FIRST and DATA)
    if town_menu_choice == "b": # (B)uy stuff
        show_shop_menu() # Need to include input for current pickaxe level
        shop_menu_choice = validate_input("Your choice? ", r"^[p|b|l]$")
        # purchasing mechanic
    elif town_menu_choice == "v":
        save_game()
    

print("Thanks for playing")