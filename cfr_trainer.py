# cfr_trainer.py

class CFRTrainer:
    def __init__(self):
        # Regrets cumulés par information set (ici l'historique des actions)
        self.regret_sum = {}
        # Somme cumulée des stratégies pour obtenir la stratégie moyenne
        self.strategy_sum = {}
        # Définition de l'arbre d'actions pour chaque information set
        self.actions = {
            "": ["bet", "check"],
            "bet": ["call", "fold"],
            "check": ["bet", "check"],
            "check-bet": ["call", "fold"]
        }

    def get_strategy(self, info_set, reach_weight):
        """Calcule et retourne la stratégie courante pour un information set."""
        regrets = self.regret_sum.get(info_set, {a: 0 for a in self.actions[info_set]})
        normalizing_sum = 0
        strategy = {}
        for a in self.actions[info_set]:
            strategy[a] = regrets[a] if regrets[a] > 0 else 0
            normalizing_sum += strategy[a]
        if normalizing_sum > 0:
            for a in self.actions[info_set]:
                strategy[a] /= normalizing_sum
        else:
            for a in self.actions[info_set]:
                strategy[a] = 1 / len(self.actions[info_set])
        # Cumuler la stratégie pour le calcul de la stratégie moyenne
        if info_set not in self.strategy_sum:
            self.strategy_sum[info_set] = {a: 0 for a in self.actions[info_set]}
        for a in self.actions[info_set]:
            self.strategy_sum[info_set][a] += reach_weight * strategy[a]
        return strategy

    def terminal_util(self, history):
        """Retourne l'utilité terminale pour un état donné."""
        if history == "bet-fold":
            return 1    # Gain pour le joueur 0
        elif history == "bet-call":
            return 0
        elif history == "check-check":
            return 0
        elif history == "check-bet-call":
            return 0
        elif history == "check-bet-fold":
            return -1   # Perte pour le joueur 0
        return None

    def cfr(self, history, p0, p1):
        """
        Algorithme CFR récursif.
        history : chaîne représentant la séquence d'actions.
        p0, p1 : probabilités de réalisation pour les joueurs 0 et 1.
        """
        util = self.terminal_util(history)
        if util is not None:
            return util

        # Déterminer le joueur courant en fonction de l'historique
        if history == "" or history == "check-bet":
            curr_player = 0
        else:
            curr_player = 1

        info_set = history  # On utilise l'historique comme identifiant d'information set
        strategy = self.get_strategy(info_set, p0 if curr_player == 0 else p1)
        node_util = 0
        util_map = {}
        for a in self.actions[info_set]:
            next_history = history + ("-" if history else "") + a
            if curr_player == 0:
                util_map[a] = -self.cfr(next_history, p0 * strategy[a], p1)
            else:
                util_map[a] = -self.cfr(next_history, p0, p1 * strategy[a])
            node_util += strategy[a] * util_map[a]
        
        # Mise à jour des regrets
        for a in self.actions[info_set]:
            regret = util_map[a] - node_util
            if curr_player == 0:
                self.regret_sum.setdefault(info_set, {x: 0 for x in self.actions[info_set]})
                self.regret_sum[info_set][a] += p1 * regret
            else:
                self.regret_sum.setdefault(info_set, {x: 0 for x in self.actions[info_set]})
                self.regret_sum[info_set][a] += p0 * regret
        return node_util

    def train(self, iterations):
        """Entraîne le CFR sur un nombre d'itérations donné."""
        util = 0
        for i in range(iterations):
            util += self.cfr("", 1, 1)
        print("Utilité moyenne pour le joueur 0 après entraînement :", util / iterations)

    def get_average_strategy(self):
        """Calcule et retourne la stratégie moyenne pour chaque information set."""
        avg_strategy = {}
        for info_set, action_sums in self.strategy_sum.items():
            normalizing_sum = sum(action_sums.values())
            avg_strategy[info_set] = {}
            for a, value in action_sums.items():
                if normalizing_sum > 0:
                    avg_strategy[info_set][a] = value / normalizing_sum
                else:
                    avg_strategy[info_set][a] = 1 / len(self.actions[info_set])
        return avg_strategy

if __name__ == "__main__":
    trainer = CFRTrainer()
    trainer.train(10000)
    avg_strategy = trainer.get_average_strategy()
    print("Stratégies moyennes obtenues :")
    for info_set, strategy in avg_strategy.items():
        print(f"{info_set}: {strategy}")