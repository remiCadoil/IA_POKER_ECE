import random
import itertools

class TexasHoldemEnv:
    def __init__(self, bet_amount=10):
        self.bet_amount = bet_amount
        self.suits = ['H', 'D', 'C', 'S']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
        self.deck = []
        self.player_hands = {0: [], 1: []}
        self.community_cards = []
        self.pot = 0
        self.active_players = [0, 1]
        self.phase = 'preflop'
    
    def reset(self):
        """Réinitialise l'environnement pour une nouvelle partie."""
        self.deck = [r + s for r in self.ranks for s in self.suits]
        random.shuffle(self.deck)
        self.player_hands = {0: [], 1: []}
        self.community_cards = []
        self.pot = 0
        self.active_players = [0, 1]
        self.phase = 'preflop'
        # Distribuer 2 cartes à chaque joueur
        for player in [0, 1]:
            self.player_hands[player] = [self.deck.pop(), self.deck.pop()]
        return self.get_state()

    def deal_community_cards(self, n):
        """Distribue n cartes du deck vers les cartes communes."""
        cards = []
        for _ in range(n):
            cards.append(self.deck.pop())
        self.community_cards.extend(cards)

    def get_state(self):
        """Retourne l'état actuel de la partie."""
        return {
            'phase': self.phase,
            'player_hands': self.player_hands,
            'community_cards': self.community_cards,
            'pot': self.pot,
            'active_players': self.active_players
        }
    
    def run_betting_round(self, actions):
        """
        Simule un tour d'enchères simplifié.
        Paramètre 'actions' : liste de tuples (player, action).
        Actions autorisées : 'check', 'bet', 'call', 'fold'
        
        Logique simplifiée :
          - Si le premier joueur mise ('bet'), le second doit 'call' ou 'fold'.
          - Si le premier joueur check, le second peut soit 'check', soit 'bet'.
            Si le second mise, le premier doit répondre par 'call' ou 'fold'.
        """
        if len(actions) < 2:
            print("Il faut au moins deux actions pour un tour d'enchères.")
            return

        # Première action
        first_player, first_action = actions[0]
        if first_action == 'bet':
            self.pot += self.bet_amount
            print(f"Joueur {first_player} mise {self.bet_amount}.")
            # La réponse du second joueur
            second_player, second_action = actions[1]
            if second_action == 'call':
                self.pot += self.bet_amount
                print(f"Joueur {second_player} suit la mise de {self.bet_amount}.")
            elif second_action == 'fold':
                print(f"Joueur {second_player} se couche.")
                if second_player in self.active_players:
                    self.active_players.remove(second_player)
                return
            else:
                print("Action invalide après une mise.")
        elif first_action == 'check':
            print(f"Joueur {first_player} check.")
            # Action du second joueur
            second_player, second_action = actions[1]
            if second_action == 'bet':
                self.pot += self.bet_amount
                print(f"Joueur {second_player} mise {self.bet_amount}.")
                # Attente de la réponse du premier joueur
                if len(actions) < 3:
                    print("Réponse attendue du Joueur {} après la mise.".format(first_player))
                    return
                third_player, third_action = actions[2]
                if third_action == 'call':
                    self.pot += self.bet_amount
                    print(f"Joueur {third_player} suit la mise de {self.bet_amount}.")
                elif third_action == 'fold':
                    print(f"Joueur {third_player} se couche.")
                    if third_player in self.active_players:
                        self.active_players.remove(third_player)
                    return
                else:
                    print("Action invalide en réponse à une mise.")
            elif second_action == 'check':
                print(f"Joueur {second_player} check.")
            else:
                print("Action invalide pour le second joueur.")
        else:
            print("Première action invalide.")

    def evaluate_hand(self, cards):
        """
        Évalue naïvement la force d'une main en calculant la somme maximale 
        des valeurs des 5 cartes parmi l'ensemble des cartes (main + cartes communes).
        La valeur des cartes : '2'-'9' -> 2-9, 'T' -> 10, 'J' -> 11, 'Q' -> 12, 'K' -> 13, 'A' -> 14.
        """
        rank_value = {r: i for i, r in enumerate(['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'], start=2)}
        best = 0
        # Si moins de 5 cartes, on somme toutes les valeurs
        if len(cards) < 5:
            return sum(rank_value[card[0]] for card in cards)
        for comb in itertools.combinations(cards, 5):
            total = sum(rank_value[card[0]] for card in comb)
            if total > best:
                best = total
        return best

    def showdown(self):
        """
        Effectue le dénouement de la partie.
        Évalue la force de la main (cartes privées + community_cards) pour chaque joueur encore en lice.
        Retourne la liste des gagnants (en cas d'égalité) et la force de leur main.
        """
        scores = {}
        for player in self.active_players:
            combined = self.player_hands[player] + self.community_cards
            score = self.evaluate_hand(combined)
            scores[player] = score
            print(f"Joueur {player} score de main : {score}")
        max_score = max(scores.values())
        winners = [player for player, score in scores.items() if score == max_score]
        return winners, max_score

    def play_round(self, betting_actions):
        """
        Simule une partie complète de Texas Hold'em.
        
        Paramètre 'betting_actions' : dictionnaire dont les clés sont les phases ('preflop', 'flop', 'turn', 'river')
        et les valeurs sont les listes d'actions à exécuter pour chaque phase.
        """
        # Préflop
        print("=== Tour d'enchères Préflop ===")
        if len(self.active_players) > 1 and 'preflop' in betting_actions:
            self.run_betting_round(betting_actions['preflop'])
        else:
            print("Aucune action préflop ou un seul joueur actif.")

        # Flop
        if len(self.active_players) > 1:
            self.phase = 'flop'
            self.deal_community_cards(3)
            print(f"Cartes du Flop : {self.community_cards}")
            if 'flop' in betting_actions:
                print("=== Tour d'enchères Flop ===")
                self.run_betting_round(betting_actions['flop'])

        # Turn
        if len(self.active_players) > 1:
            self.phase = 'turn'
            self.deal_community_cards(1)
            print(f"Carte du Turn : {self.community_cards[-1]}")
            if 'turn' in betting_actions:
                print("=== Tour d'enchères Turn ===")
                self.run_betting_round(betting_actions['turn'])

        # River
        if len(self.active_players) > 1:
            self.phase = 'river'
            self.deal_community_cards(1)
            print(f"Carte du River : {self.community_cards[-1]}")
            if 'river' in betting_actions:
                print("=== Tour d'enchères River ===")
                self.run_betting_round(betting_actions['river'])

        # Showdown
        if len(self.active_players) > 1:
            self.phase = 'showdown'
            print("=== Showdown ===")
            winners, score = self.showdown()
            print(f"Gagnant(s) : {winners} avec un score de {score}")
        else:
            print("La manche s'est terminée prématurément suite à un fold.")

        print(f"Total du pot : {self.pot}")
        return self.get_state()


# --- Exemple d'utilisation de l'environnement ---

if __name__ == "__main__":
    # Création de l'environnement
    env = TexasHoldemEnv(bet_amount=10)
    state = env.reset()
    print("État initial :")
    print(state)
    
    # Définition des actions de chaque tour d'enchères
    betting_actions = {
        'preflop': [(0, 'check'), (1, 'bet'), (0, 'call')],
        'flop': [(0, 'bet'), (1, 'call')],
        'turn': [(0, 'check'), (1, 'check')],
        'river': [(0, 'bet'), (1, 'call')]
    }
    
    # Jouer une manche complète
    final_state = env.play_round(betting_actions)
    print("État final de la partie :")
    print(final_state)