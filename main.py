# main.py

from environment import TexasHoldemEnv
from cfr_trainer import CFRTrainer

def run_simulation():
    # Création de l'environnement et simulation d'une partie de Texas Hold'em
    env = TexasHoldemEnv(bet_amount=10)
    state = env.reset()
    print("=== État initial de la partie ===")
    print(state)
    
    # Exemple d'actions pour chaque phase
    betting_actions = {
        'preflop': [(0, 'check'), (1, 'bet'), (0, 'call')],
        'flop': [(0, 'bet'), (1, 'call')],
        'turn': [(0, 'check'), (1, 'check')],
        'river': [(0, 'bet'), (1, 'call')]
    }
    
    print("\n=== Déroulement de la partie ===")
    final_state = env.play_round(betting_actions)
    print("\nÉtat final de la partie :")
    print(final_state)

def run_cfr_training():
    # Entraînement de l'algorithme CFR sur l'arbre simplifié
    trainer = CFRTrainer()
    trainer.train(10000)
    avg_strategy = trainer.get_average_strategy()
    print("\nStratégies moyennes obtenues par CFR :")
    for info_set, strategy in avg_strategy.items():
        print(f"{info_set}: {strategy}")

if __name__ == "__main__":
    print("=== Simulation de l'environnement Texas Hold'em ===")
    run_simulation()
    
    print("\n=== Entraînement CFR sur arbre de décision simplifié ===")
    run_cfr_training()