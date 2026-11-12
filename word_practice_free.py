import re
import os
import requests
import time
from urllib.parse import quote
from colorama import Fore, Style, init

# Initialize colorama to work with ANSI escape sequences on Windows
init(autoreset=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_word_input():
    while True:
        word = input("\nEnter an English word or phrase (lowercase only): ")
        if re.match("^[a-z ]+$", word):
            return word
        else:
            print(Fore.RED + "\nInvalid input. Please use only lowercase letters and spaces.")

def get_word_details(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None, []

    if not isinstance(data, list) or not data:
        return None, []

    entry = data[0]
    phonetics = entry.get("phonetics", [])

    for meaning in entry.get("meanings", []):
        for item in meaning.get("definitions", []):
            definition = item.get("definition")
            if definition:
                return definition, phonetics

    return None, phonetics


def play_game(word, level, total_coins, definition, phonetics):
    
    coins_earned = 0
    incorrect_letters = False
    strike_pattern = True  # Initialize strike pattern flag    
    strike = 0  # Initialize the strike count

    
    if level == 1:
        display_word = ''.join(['_' if c in 'aeiou' else c for c in word])
        answer = ''.join([c if c in 'aeiou' else '_' for c in word])
        prompt = "\nEnter the missing letter"
    elif level == 2:
        display_word = ''.join(['_' if c not in 'aeiou' else c for c in word])
        answer = ''.join([c if c not in 'aeiou' else '_' for c in word])
        prompt = "\nEnter the missing letter"
    elif level == 3:
        display_word = word[0] + '_' * (len(word) - 2) + word[-1]
        answer = word
        prompt = "\nEnter the missing letter"
    elif level == 4:
        display_word = word[0] + '_' * (len(word) - 1)
        answer = word
        prompt = "\nEnter the missing letter"
    else:
        display_word = '_' * len(word)
        answer = word
        prompt = "\nEnter the missing letter"
    
    print(Fore.CYAN + "\nComplete the word:", display_word)
    
    
    for i in range(len(answer)):
        if display_word[i] == '_':
            while True:
                guess = input(f"{prompt} {i + 1}: ")
                if guess == answer[i]:
                    display_word = display_word[:i] + answer[i] + display_word[i + 1:]
                    strike += 1  # Increase strike count for the next correct letter
                    coins_earned = strike  # Update coins_earned with the current strike count
                    total_coins += coins_earned
                    dancing_animation(level, total_coins, definition, phonetics)  # Update level, sack, coins earned, and total coins
                    
                    print(Fore.CYAN + "\nComplete the word:", display_word)
                    print(Fore.GREEN + f"\nCorrect! Coins earned for this letter: {coins_earned}")
                    break
                else:
                    strike = 0  # Reset strike if incorrect letter is entered
                    coins_earned = 0  # Reset coins_earned
                    dancing_animation(level, total_coins, definition, phonetics)  # Update level, sack, coins earned, and total coins
                    
                    print(Fore.CYAN + "\nComplete the word:", display_word)
                    print(Fore.RED + f"\nIncorrect. Try again. Coins earned for this letter: {coins_earned}")
                    strike_pattern = False  # If incorrect letter, no strike pattern
                    incorrect_letters = True  # Incorrect letters entered

    if strike_pattern and strike > 1:  # Display "STRIKE!" if there is a strike (strike > 1)
        print(Fore.MAGENTA + "\nSTRIKE!")
    
    print("\nCongratulations! You completed the word:", word)
 
    return coins_earned, total_coins, incorrect_letters  # Return coins earned for this level and total_coins


def main():
    while True:
        word = get_word_input()
        definition, phonetics = get_word_details(word)

        if len(word) <= 3 or definition is None:
            if len(word) <= 3:
                print(Fore.RED + "\nPlease enter a word with more than 3 letters.")
            else:
                print(Fore.RED + "\nDefinition not found or the dictionary service is unavailable. Please try another word.")
            input("\nPress Enter to continue...")
            clear_screen()
        else:
            clear_screen()  # Clear the screen before starting level 1
            break
    
    # Read the highest score from the file or set it to 0
    highest_score = read_highest_score()

    total_coins = 0
    coins_earned = 0
    mega_strike = True  # Initialize mega strike flag    

    for level in range(1, 6):
        print(f"\n--- Level {level} ---")
        dancing_animation(level, total_coins, definition, phonetics)  # Display level, sack, coins earned, and total coins
        coins_earned, total_coins, incorrect_letters = play_game(word, level, total_coins, definition, phonetics)  # Pass coins_earned and total_coins
        if incorrect_letters:
            mega_strike = False  # If incorrect letters entered, no mega strike        
        input(Fore.GREEN + "\nPress Enter to continue...")
        clear_screen()

    dancing_animation(5, total_coins,definition, phonetics)  # Display total coins at the end
    print(Fore.GREEN + "\nCongratulations! You have completed all levels!")
    if mega_strike:
        print(Fore.MAGENTA + "\nMEGA STRIKE!")
    
        # Check if the current game's total coins is the highest score
    if total_coins > highest_score:
        highest_score = total_coins
        save_highest_score(highest_score)  # Save the new highest score

    print(f"\nYou have earned {Fore.YELLOW}{total_coins}{Style.RESET_ALL} coins!")

        # Display "New Highest Score!" if applicable
    if total_coins == highest_score:
        print(Fore.GREEN + "New Highest Score!")
    
    while True:
        choice = input("\nDo you want to enter another word? (yes/no): ").lower()
        if choice == "yes":
            clear_screen()
            main()
        elif choice == "no":
            print("\nThank you for playing!\n")
            break
        else:
            print(Fore.RED + "Invalid input. Please enter 'yes' or 'no'.")


def dancing_animation(level, total_coins, definition, phonetics):
    cat_sack = r"""
 /\_/\  
( o.o ) 
 > ^ <
/  ^  \
|_______|
"""
    sack_with_coins = "|{}|".format(Fore.YELLOW + "$" * total_coins)  # Create sack with dollar signs
    cat_sack_with_sack = cat_sack.replace("|_______|", sack_with_coins)  # Replace sack in animation
    clear_screen()
    print(Fore.RED + cat_sack_with_sack)
    print(f"\nLevel {level}")
    print(f"Total coins: {Fore.YELLOW}{total_coins}{Style.RESET_ALL}")
    print("\nDefinition:", definition)

    phonetic_text = ""

    if phonetics:
        if len(phonetics) > 1 and 'text' in phonetics[1]:
            phonetic_text = phonetics[1]['text']
        elif len(phonetics) > 0 and 'text' in phonetics[0]:
            phonetic_text = phonetics[0]['text']

    print("Phonetics:", phonetic_text)

def read_highest_score():
    try:
        with open("highest_score.txt", "r") as file:
            content = file.read().strip()
            if content:
                highest_score = int(content)
                return highest_score
            else:
                return 0
    except FileNotFoundError:
        return 0

def save_highest_score(score):
    with open("highest_score.txt", "w") as file:
        file.write(str(score))

if __name__ == "__main__":
    main()