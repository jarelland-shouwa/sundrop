from random import randint
import os

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
    # initialize map
    try:
        load_map("level1.txt")
    except FileNotFoundError:
        print("FileNotFoundError; Please check the level map exists again")

    # TODO: initialize fog
    
    # TODO: initialize player
    #   You will probably add other entries into the player dictionary
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

    # Creating the save directory (ensures save directory exists in working directory)
    # Source: https://www.geeksforgeeks.org/python/create-a-directory-in-python/
    directory_name = "saves"

    try: # The exceptions are only for debugging
        os.mkdir(directory_name)
        # print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    save_game()
    
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
def save_game(game_map: list = game_map, fog = [], player: dict = player) -> None: # default values
    '''This function saves the game'''
    directory_name = "saves"

    # save map
    # Saving map list
    save_file_map = open(f"{directory_name}\save_1_map.txt", "w")
    text_to_write = ""
    for row in game_map:
        for element in row:
            text_to_write += element
        text_to_write += "\n"
    text_to_write = text_to_write[:len(text_to_write)-1]
    save_file_map.write(text_to_write)
    save_file_map.close()

    # save fog

    # save player
    # Saving str and int
    save_file_player = open(f"{directory_name}\save_1_player.txt", "w")
    text_to_write = ""
    for key in player.keys():
        if type(player[key]) == str or type(player[key]) == int:
            text_to_write += f"{key},{player[key]}\n"
    text_to_write = text_to_write[:len(text_to_write)-1]
    save_file_player.write(text_to_write)
    save_file_player.close()

    # return
        
# This function loads the game
def load_game(game_map: list = game_map, fog = [], player: dict = player) -> bool: # default values
    '''This function loads the game'''
    directory_name = "saves"

    try:
        # load map
        load_map(f"{directory_name}/save_1_map.txt")
        # print(f"game_map: {game_map}")

        # load fog

        # load player
        player.clear()
        save_file_player = open(f"{directory_name}/save_1_player.txt", "r")
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
            except TypeError:
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


def validate_input(message: str, constraints: str) -> str: # need to typecast in main code when working outside of strings
    while True:
        user_input = input(message).lower()
        if user_input in constraints:
            return user_input
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
    main_menu_choice = validate_input("Your choice? ","nlq")

    if main_menu_choice == "n":
        name = input("Greetings, miner! What is your name? ")
        print(f"Pleased to meet you, {name}. Welcome to Sundrop Town!")
        initialize_game()
        save_game()
        load_game()
    elif main_menu_choice == "l":
        loaded_success = load_game()
        if not loaded_success:
            continue
    elif main_menu_choice == "q":
        break
    
    show_town_menu()
    town_menu_choice = validate_input("Your choice? ", "bimevq")
    
    # DON'T TOUCH BELOW YET (DEAL WITH SAVING MECHANIC FIRST and DATA)
    if town_menu_choice == "b": # (B)uy stuff
        show_shop_menu() # Need to include input for current pickaxe level
        shop_menu_choice = validate_input("Your choice? ", "pbl")
        # purchasing mechanic
    elif town_menu_choice == "v":
        save_game()
    

print("Thanks for playing")