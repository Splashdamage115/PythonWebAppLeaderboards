import cards
import random

def playersHand():
    print("\n\tPlayer's hand: ")
    for n, card in enumerate(player):
        print(f"\t\t{n} --> {card}")

deck = cards.generateDeck()

computer = []
player = []

for _ in range(7):
    computer.append(deck.pop())
    player.append(deck.pop())



player_pairs = []
computer_pairs = []


player, pairs = cards.identify_remove_pairs(player)
player_pairs.extend(pairs)
computer, pairs = cards.identify_remove_pairs(computer)
computer_pairs.extend(pairs)

while True:
    player.sort()

    print(f"Here are your current cards:\n{player}\n")
    ## print(f"Here are the computers current cards:\n{computer}")

    playersHand()
    
    choice = input("\n\nPlease select the number for the card you want from the above list")
    selection = player[ int(choice) ]
    value = selection[: selection.find(" ")]
    
    found_it = False
    for n, card in enumerate(computer):
        if card.startswith(value):
            found_it = n
            break
    
    
    if isinstance(found_it, bool):
        # go fish code
        print("\nGo Fish\n")
        player.append(deck.pop())
        print(f"You drew a {player[-1]}")
        if len(deck) == 0:
            break
    else:
        # swap code
        print(f"Here is your card: {computer[n]}.")
        player.append(computer.pop(n))
    
    player, pairs = cards.identify_remove_pairs(player)
    player_pairs.extend(pairs)
    
    
    if len(player) == 0:
        print("The game is over. The player Won!")
        break
    if len(computer) == 0:
        print("The game is over. The computer Won!")
        break
    
    playersHand()
    
    card = random.choice(computer)
    value = card[: card.find(" ")]
    
    choice = input(f"\nFrom the computer: Do you have a {value}? (y/n) ")
    
    if choice in ["y", "Y", "yes", "Yes", "YES"]:
        # swap code
        for n, card in enumerate(player):
            if card.startswith(value):
                break
    
        computer.append(player.pop(n))
    else:
        # go fish code
        computer.append(deck.pop())
        if len(deck) == 0:
            break
        
    computer, pairs = cards.identify_remove_pairs(computer)
    computer_pairs.extend(pairs)
    
    if len(computer) == 0:
        print("The game is over. The computer Won!")
        break
    if len(player) == 0:
        print("The game is over. The player Won!")
        break

## who has won??
if len(deck) == 0:
    print("Game over. Deck is Empty!")
    if len(player_pairs) == len(computer_pairs):
        print("It's a Draw")
    elif len(player_pairs) > len(computer_pairs):
        print("The game is over. The player Won!")
    else:
        print("The game is over. The computer Won!")