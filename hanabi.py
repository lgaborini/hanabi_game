# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import events

import random
from termcolor import colored

import logging
import progressbar
import csv

import argparse


# Set-up logging
logging.getLogger('').handlers.clear()
loglevel = logging.WARNING
logging.basicConfig(filename = 'hanabi.log', filemode = 'w',
                    level = loglevel, 
                    format = '[%(levelname)6s]: %(message)s')

console = logging.StreamHandler()
console.setLevel(logging.root.level)

logging.getLogger('').addHandler(console)



# Global variables
colors = ('red', 'green', 'yellow', 'white', 'cyan')
numbers = (1, 2, 3, 4, 5)
quantities = (3, 2, 2, 2, 1)


    
class Card:
    """A Hanabi card. Has number and color."""
    
    def __init__(self, number, color):
        self.number = number
        self.color = color
    
    def __str__(self):
        return colored(self.number, self.color)
    
        
class CardStack:
    """A stack of Hanabi cards. Similar to a list."""

    def __init__(self, cards = None):
        if cards is None:
            cards = []
        self.cards = cards
    
    def __str__(self):
        s = ''.join(str(x) for x in self.cards)
        return s
    
    def append(self, c):
        self.cards.append(c)
        
    def shuffle(self):
        random.shuffle(self.cards)
        
    def pop(self, idx = -1):
        if self.cards:
            return self.cards.pop(idx)
        else:
            raise events.CardError("No more cards to pick.")
            
    def top(self):
        if (self.cards):
            return self.cards[-1]
        else:
            return None
        
    def __len__(self):
        return len(self.cards)        
        
    
class Deck(CardStack):
    """A deck of Hanabi cards."""
    
    def __init__(self):
        super().__init__(cards = [])
               
        # Make the starting deck
        for c in colors:
            for n, q in zip(numbers, quantities):
                for i in range(q):
                    gc = Card(n, c)
                    self.cards.append(gc)

    def print(self):
        super().print()
        

class Pile(CardStack):
    """A monochromatic pile of Hanabi cards."""
    
    def __init__(self, color):
        super().__init__(cards = [])
        self.color = color
        
    def append(self, card):
        if card.color != self.color:
            raise events.InvalidActionError('Wrong card added!')
        super().append(card)


class Piles:
    """All Hanabi cards piles."""
    
    def __init__(self):

        # Make the piles
        self.piles = dict((c, None) for c in colors)        
        for c in colors:
            # Add bogus card with 0 value to the pile
            card = Card(0, c)
            pile = Pile(c)
            pile.append(card)
            self.piles[c] = pile
    
    def append(self, card):
        """Attempt to add a card to the matching pile."""
        can_play = self.is_playable(card)
        
        target_pile = self.piles[card.color]
        card_on_top = target_pile.top()
        
        if can_play:
            target_pile.append(card) 
            logging.debug('Appended card {0} to pile {1}.'.format(card, card_on_top))
        else:
            raise events.WrongPlayError('ERROR Tried to play a wrong card: {0} on pile {1}.'.format(card, card_on_top))
        
        if card.number == 5:
            raise events.CompletedPile('Completed {0} pile! +1 hint.'.format(card.color))
        
    def is_playable(self, card):
        """Return whether a card can be played."""
        
        target_pile = self.piles.get(card.color)
        card_on_top = target_pile.top()
        
        if card_on_top is None or card.number == card_on_top.number + 1:
            return True
        else:
            return False
        
    def __str__(self):
        cards = []
        
        for color in self.piles:
            card_to_print = self.piles[color].top()
            cards.append(card_to_print)
        
        s = ''.join(str(c) for c in cards)
        return s
        
    def score(self):
        total = 0
        for c in self.piles:
            card_on_top = self.piles[c].top()
            if card_on_top:
                total += card_on_top.number
        return total




class Player:
    """A Hanabi player."""
    
    def __init__(self, name):
        self.hand = CardStack()
        self.name = name
        
    def remove_card(self, idx = None):

        try:
            if idx is None:
                card = self.hand.pop()
            else:
                card = self.hand.pop(idx)
                
            return card
        
        except IndexError:
            raise events.InvalidActionError('Wrong action: card not in hand')
            
        except events.CardError:
            raise events.CardError('Player {0}: no more cards in hand.'.format(self.name))
    
    def print(self):
        logging.info('Player {0}: hand {1}'.format(self.name, self.hand))
        
    def __str__(self):
        return str(self.hand)
        
    
class Game:
    
    def __init__(self, play_strategy = None):
        
        if play_strategy is None:
            self.play_strategy = 'best'
        else:
            self.play_strategy = play_strategy
    
    def init_game(self):
        
        self.hints = 7
        self.errors = 3
        self.n_players = 3
        self.deck = Deck()
        self.piles = Piles()
        self.players = []        
        
        
    def game_loop(self):
        
        self.init_game()
        
        # Shuffle deck and give hands
        self.deck.shuffle()
        for p in range(self.n_players):
            pl = Player(p + 1)
            self.players.append(pl)

            for nc in range(5):
                c = self.deck.pop()
                self.players[p].hand.append(c)

        logging.info('Starting game')
        self.print()
        
        is_last_turn = False
        turn = 1      
        turns_left = self.n_players
        
        actions = ('play', 'hint', 'discard')
        while True:
            logging.info('')
            logging.info('*** Turn {0} ***'.format(turn))
            
            for p in self.players:
                successful = False
                logging.info('')
                logging.info('    Player {0}'.format(p.name))
             
                # Print the game status
                self.print()                
                                    
                tries = 0
                while not successful:
                    try:
                        tries = tries + 1
                        if tries > 20:
                            raise events.HanabiError('Too many tries!')
                            
                        action = random.choice(actions)
                        logging.debug('Try {0}: trying action {1}'.format(tries, action))
                        if action == 'play':
                            self.play(p)
                        elif action == 'hint':
                            self.hint()
                        else:
                            self.discard(p)
                            
                    except events.InvalidActionError as e:
                        logging.debug(e)
                        continue
                    
                    except events.WrongPlayError as e:
                        logging.debug(e)
                        
                        if e.is_game_error:
                            self.errors = self.errors - 1
                            
                        if self.errors == 0:
                            score = self.piles.score()
                            logging.info('Game ended with defeat. Score = {}'.format(score))
                            return {'finished': False, 'score': score, 'turns': turn}
                        
                    except events.EmptyDeck as e:
                        logging.debug(e)
                        successful = True           
                        
                    except events.CardError as e:
                        logging.debug(e)
                        continue
                      
                    except events.CompletedPile:
                        self.hints = self.hints + 1
                        successful = True
                        
                    except Exception as e:
                        logging.warning('Uncaught exception: {}'.format(e))
                        raise
                    
                    successful = True
                        
                    
                # A valid action has been chosen
                logging.debug('Player {0} chose action: "{1}".'.format(p.name, action))
                
                # Draw a card
                try:
                    if action in ('play', 'discard'):
                        card = self.deck.pop()
                        p.hand.append(card)
                        logging.debug('Player {0} picks a card: {1}'.format(p.name, card))
                        
                except events.CardError as e:
                    logging.info('Last turn!')
                    is_last_turn = True
                
                except:
                    raise
                    
                if turn > 35:
                    raise events.HanabiError('Too many turns! Loop?')
    
            
                if is_last_turn:
                    turns_left = turns_left - 1
                    
                if turns_left == 0:
                    score = self.piles.score()
                    logging.info('Game ended successfully! Score = {}'.format(score))
                    self.print()
                    return {'finished': True, 'score': score, 'turns': turn}
            
            # Out of player loop
            turn = turn + 1
                    
        
    def discard(self, player):
        if self.hints < 7:
            self.hints = self.hints + 1
            try:
                card = player.remove_card()
                logging.debug('Player {0} discards a {1}'.format(player.name, card))
            except events.CardError as e:
                logging.debug(e)
                raise events.CardError('Cannot discard: {0}\'s hand is empty'.format(player.name))
            except:
                raise
        else:
            raise events.InvalidActionError('Cannot discard: already full hints')
            
    def play(self, player):
        
        if len(player.hand) == 0:
            raise events.InvalidActionError('Player {0}: no more cards in hand.'.format(player.name))

        if self.play_strategy == 'best':
            found_card = False 
            for idx, card in enumerate(player.hand.cards):
                
                if self.piles.is_playable(card):
                    logging.debug('Player {0}: found playable card {1}.'.format(player.name, card))
                    card = player.remove_card(idx)
                    found_card = True
                    break
                
        if self.play_strategy == 'random' or not found_card:
            card = player.remove_card()
            logging.debug('Player {0}: playing card {1} randomly (strategy: {2}).'.format(player.name, card, self.play_strategy))        
        else:
            logging.debug('Player {0}: playing card {1} (strategy: {2}).'.format(player.name, card, self.play_strategy))        

        self.piles.append(card)
        
    def hint(self):
        if self.hints > 0:
            self.hints = self.hints - 1
        else:
            raise events.InvalidActionError('Cannot hive hint: no more hints.')
              
    def print(self):
        for p in self.players:
            p.print()
        
        logging.info('Piles: {0}. Score: {1}'.format(self.piles, self.piles.score()))
        logging.info('{0} cards left in deck, {1} hint(s) left, {2} error(s) left.'.format(
                len(self.deck.cards),
                self.hints, 
                self.errors))
    
        

def multi_run(game, how_many):
    results = [None] * how_many
    with progressbar.ProgressBar(max_value = how_many) as bar:
        for i in range(how_many):
            logging.info('')
            logging.info('Game {}'.format(i + 1))
            results[i] = game.game_loop()
            bar.update(i)
    return results
            
        
def main(how_many = 100):
#    player = Player(1)
#    player.remove_card()
    game = Game()
    
    scores = multi_run(game, how_many)
#    scores.sort()
#    scores.sort(key = lambda x: x[1])
    return scores


def debug_players():
    deck = Deck()
    print('The deck')
    print(deck)
    
    # Making players
    p1 = Player(1)
    for i in range(5):
        c1 = deck.pop()
        p1.hand.append(c1)
        
    p2 = Player(2)
    for i in range(5):
        c2 = deck.pop()
        p2.hand.append(c2)
    
    print("Player 1:", p1)
    print("Player 2:", p2)
    
    print('The deck')
    print(deck)
    
    deck.shuffle()

    print(deck)


def parseArguments():
    # Create argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("how_many", type = int, help = "How many games are simulated", default = 1000, nargs='?')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    
    args = parseArguments()
    
    scores = main(args.how_many)
    
    with open('scores.csv', 'w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = scores[0].keys())
        writer.writeheader()
        writer.writerows(scores)
    
    print('Scores:')
    print(scores)
    quit
    