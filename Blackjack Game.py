# Blackjack Game

import random
import os
import pygame
from colorama import init, Fore

# Initialize Pygame mixer for playing sounds and Colorama for using colours
pygame.mixer.init()
init(autoreset=True)

# Emojis for card suits
suits = {
    "hearts": f"{Fore.RED}❤️", 
    "diamonds": f"{Fore.RED}♦️", 
    "clubs": f"{Fore.BLACK}♣️", 
    "spades": f"{Fore.BLACK}♠️"
}
card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11}

# Load sounds
def play_event_sound(event):
    if event == "deal":
        pygame.mixer.music.load('deal.mp3')
    elif event == "win":
        pygame.mixer.music.load('win.mp3')
    elif event == "lose":
        pygame.mixer.music.load('lose.mp3')
    elif event == "tie":
        pygame.mixer.music.load('lose.mp3')
    pygame.mixer.music.play()

# Create and shuffle deck
def create_deck():
    deck = []
    for suit in suits:
        for value in card_values:
            deck.append(f'{value} of {suit}')
    return deck

def shuffle_deck_with_sound(deck):
    random.shuffle(deck)
    play_event_sound('deal')  # Play shuffle sound

# Deal a card from the deck
def deal_card(deck):
    return deck.pop()

# Calculate hand value
def calculate_hand_value(hand):
    value = 0
    ace_count = 0
    for card in hand:
        card_value = card.split()[0]  # Extract card value (e.g., '2', 'J', 'A')
        value += card_values[card_value]
        if card_value == 'A': # aces can be either 1 or 11, depending on the other cards the player is holding
            ace_count += 1
    while value > 21 and ace_count:
        value -= 10
        ace_count -= 1
    return value

# Display hand
def display_hand(hand, is_dealer=False):
    hand_str = " ".join([f"{card.split()[0]} {suits[card.split()[2]]}" for card in hand])
    print(f"{'Dealer' if is_dealer else 'Player'}'s hand: {hand_str} (Value: {calculate_hand_value(hand)})")

# Check if player wants to split
def check_split(player_hand):
    if len(player_hand) == 2 and card_values[player_hand[0].split()[0]] == card_values[player_hand[1].split()[0]]:
        return True
    return False

# Check if player wants to double down
def check_double_down(balance):
    if balance >= 5:  # Ensure the player has enough balance to double down
        double_down_choice = input(f"Do you want to double down? (y/n): ").lower()
        if double_down_choice == 'y':
            return True
    return False

# Place bet
def place_bet(balance):
    while True:
        bet = int(input(f"Your balance: ${balance}\nEnter your bet (minimum $5): "))
        if bet >= 5 and bet <= balance:
            return bet
        else:
            print(f"Invalid bet. Bet must be at least $5 and no more than your current balance.")

# Play the round for a given hand (splits)
def play_blackjack_for_hand(player_hand, dealer_hand, deck, bet, balance):
    display_hand(player_hand)
    display_hand(dealer_hand[:1], is_dealer=True)  # Only show one dealer card

    # Player's turn
    while calculate_hand_value(player_hand) < 21:
        action = input(f"Do you want to [h]it or [s]tand? ").lower()
        if action == 'h':
            player_hand.append(deal_card(deck))
            display_hand(player_hand)
        elif action == 's':
            break
        else:
            print(f"Invalid action! Please choose [h]it or [s]tand.")
    
    # Dealer's turn (must stand at 17 or higher)
    display_hand(dealer_hand, is_dealer=True)
    while calculate_hand_value(dealer_hand) < 17:
        print(f"Dealer hits!")
        dealer_hand.append(deal_card(deck))
        display_hand(dealer_hand, is_dealer=True)

    # Calculate values
    player_value = calculate_hand_value(player_hand)
    dealer_value = calculate_hand_value(dealer_hand)

    print(f"\nYour final hand: {player_value}")
    print(f"Dealer's final hand: {dealer_value}")

    # Determine winner
    if player_value > 21:
        print(f"You busted! Dealer wins.")
        play_event_sound('lose')
        balance -= bet
    elif dealer_value > 21:
        print(f"Dealer busted! You win.")
        balance += bet * 2  # Player wins and gets back double the bet
        play_event_sound('win')
    elif player_value > dealer_value:
        print(f"You win!")
        balance += bet * 2  # Player wins and gets back double the bet
        play_event_sound('win')
    elif player_value < dealer_value:
        print(f"Dealer wins.")
        play_event_sound('lose')
        balance -= bet
    else:
        print(f"It's a tie!")
        balance += bet  # Tie, player gets the bet back
        play_event_sound('tie')

    print(f"Your balance: ${balance}")
    return balance

# Function to play a round of Blackjack
def play_blackjack():
    balance = 100  # Starting balance

    while balance > 0:
        print(f"\nStarting a new round of Blackjack!")

        deck = create_deck()
        shuffle_deck_with_sound(deck)

        bet = place_bet(balance)
        balance -= bet  # Deduct bet from balance

        player_hand = [deal_card(deck), deal_card(deck)]
        dealer_hand = [deal_card(deck), deal_card(deck)]

        display_hand(player_hand)
        display_hand(dealer_hand[:1], is_dealer=True)  # Only show one dealer card

        # Option for player to split
        if check_split(player_hand):
            print(f"Splitting the hand into two...")
            balance -= bet  # Deduct the same bet for the second hand
            hand1 = [player_hand[0], deal_card(deck)]
            hand2 = [player_hand[1], deal_card(deck)]
            print(f"\nFirst hand:")
            balance = play_blackjack_for_hand(hand1, dealer_hand, deck, bet, balance)
            print(f"\nSecond hand:")
            balance = play_blackjack_for_hand(hand2, dealer_hand, deck, bet, balance)
            continue  # End the current round

        # Option for player to double down
        if check_double_down(balance):
            print(f"Doubling down!")
            bet *= 2  # Double the bet
            player_hand.append(deal_card(deck))
            display_hand(player_hand)
            # Player gets one more card and must stand
            print(f"Your final hand: {calculate_hand_value(player_hand)}")
            if calculate_hand_value(player_hand) <= 21:
                balance += bet * 2  # Player wins and gets back double the bet
                play_event_sound('win')
            else:
                play_event_sound('lose')
            continue  # End the current round
        
        # Player's turn
        while calculate_hand_value(player_hand) < 21:
            action = input(f"Do you want to [h]it or [s]tand? ").lower()
            if action == 'h':
                player_hand.append(deal_card(deck))
                display_hand(player_hand)
            elif action == 's':
                break
            else:
                print(f"Invalid action! Please choose [h]it or [s]tand.")

        # Dealer's turn (must stand at 17 or higher)
        display_hand(dealer_hand, is_dealer=True)
        while calculate_hand_value(dealer_hand) < 17:
            print(f"Dealer hits!")
            dealer_hand.append(deal_card(deck))
            display_hand(dealer_hand, is_dealer=True)

        # Calculate values
        player_value = calculate_hand_value(player_hand)
        dealer_value = calculate_hand_value(dealer_hand)

        print(f"\nYour final hand: {player_value}")
        print(f"Dealer's final hand: {dealer_value}")

        # Determine winner
        if player_value > 21:
            print(f"You busted! Dealer wins.")
            play_event_sound('lose')
            balance -= bet
        elif dealer_value > 21:
            print(f"Dealer busted! You win.")
            balance += bet * 2  # Player wins and gets back double the bet
            play_event_sound('win')
        elif player_value > dealer_value:
            print(f"You win!")
            balance += bet * 2  # Player wins and gets back double the bet
            play_event_sound('win')
        elif player_value < dealer_value:
            print(f"Dealer wins.")
            play_event_sound('lose')
            balance -= bet
        else:
            print(f"It's a tie!")
            balance += bet  # Tie, player gets the bet back
            play_event_sound('tie')

        print(f"Your balance: ${balance}")

        if balance <= 0:
            print(f"Game over! You've run out of money.")
            break

        # Ask if player wants to play another round
        if input(f"\nDo you want to play another round? (y/n): ").lower() != 'y':
            print(f"Thanks for playing!")
            break


if __name__ == "__main__":
    play_blackjack()