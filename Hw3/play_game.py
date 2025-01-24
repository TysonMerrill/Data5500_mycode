from DeckOfCards import *

# Function to calculate score and aces
def calculate_score(hand):
    score = sum(card.val for card in hand)
    # I had to have help here but the ace counter counts an ace if the value is 11 (that is the intial value)
    ace_counter = sum(1 for card in hand if card.val == 11)
    while score > 21 and ace_counter > 0: 
        score -= 10
        ace_counter -= 1
#The logic above will reduce your ace to the value of 1 if you go over 21 and reset your ace count when that happens.
    return score

# Main game logic
def play_game():
    print()
    print("Welcome to Blackjack!")
    deck = DeckOfCards()

    #Shuffling and showing of the deck
    while True:
        print()
        print("Deck before shuffled:")
        deck.print_deck()
        print()
        deck.shuffle_deck()
        print("Deck after shuffled:")
        deck.print_deck()


        # Deal two cards to the user and dealer (and showing cards)
        uhand = [deck.get_card(), deck.get_card()]
        dhand = [deck.get_card(), deck.get_card()]
        
        print()
        uscore = calculate_score(uhand)

        # Show the users hand
        print(f"Card number 1 is: {uhand[0]}")
        print(f"Card number 2 is: {uhand[1]}")
        print("Your total score is: ", uscore)

        #User playing the game
        while uscore <= 21:
            # ask user if they would like a "hit" (another card)
            hit = input("would you like a hit? y/n: ").lower()
            #Allowing the user to see new score with a new card or lose if over 21
            if hit == 'y':
                ncard = deck.get_card()
                uhand.append(ncard)
                uscore = calculate_score(uhand)
                print("Your next card is:", ncard)
                print("New total score: ", uscore)
                if uscore > 21:
                    print("Bust! You lose.")
                    break
            elif hit == 'n':
                break
            else:
                print("Invalid entry. Please input y or n.")
#Logic continues if under 21 to the dealers turn or lets you try again here
        if uscore > 21:
            again = input("Would you like to play again? y/n: ")
            if again == 'y':
                continue
            else:
                print("Have a great day!")
                break
        
        # Show the dealers hand
        print()
        dscore = calculate_score(dhand)
        print(f"Dealers card number 1 is: {dhand[0]}")
        print(f"Dealers card number 2 is: {dhand[1]}")
        print("Dealers total score is: ", dscore)
#Making the dealer draw until at least 17
        while dscore < 17:
            ncard = deck.get_card()
            dhand.append(ncard)
            dscore = calculate_score(dhand)
            print("Dealer hit and got:", ncard)
            print("Dealer's new score:", dscore)
#Letting the user know of all the outcomes (win/loss)
        if dscore > 21:
            print("Dealer Busts! You win!")
        elif uscore > dscore:
            print("Your score was higher you win!")
        elif  dscore > uscore:
            print("Dealers score was higher you lose!")
        else:
            print("Its a tie. Sorry")
#Letting them play again
        again = input("Would you like to play again? y/n: ")
        if again == 'y':
            continue 
        else:
            print("Have a great day!")
            break

play_game()