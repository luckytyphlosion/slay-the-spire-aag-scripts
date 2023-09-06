from enum import Enum
import yaml
import itertools
import collections
import math

stance_to_damage_multiplier = {
    "exit": 1,
    "calm": 1,
    "wrath": 2,
    "divinity": 3
}

class Card:
    __slots__ = ("name", "cost", "damage", "hits", "effect")

    def __init__(self, name, cost, damage, hits, effect):
        self.name = name
        self.cost = cost
        self.damage = damage
        self.hits = hits
        self.effect = effect

    @classmethod
    def from_dict(cls, card_as_dict):
        name = card_as_dict["name"]
        cost = card_as_dict["cost"]
        damage = card_as_dict["damage"]
        hits = card_as_dict.get("hits", 1)
        effect = card_as_dict.get("effect", "none")
        return cls(name, cost, damage, hits, effect)

    def __repr__(self):
        return f"Card(name: {self.name}, cost: {self.cost}, damage: {self.damage}, hits: {self.hits}, effect: {self.effect})"

    def calc_damage(self, stance="exit", strength=0):
        return math.floor((self.damage + strength) * self.hits * stance_to_damage_multiplier[stance])

    def calc_new_stance(self, stance, enemy_attacking=True):
        if self.effect in {"wrath", "exit"}:
            return self.effect
        elif self.effect == "fearNoEvil" and enemy_attacking:
            return "calm"
        else:
            return stance

# all_effects: {'battleHymn', 'endTurn', 'wrath', 'reachHeaven', 'fearNoEvil', 'crushJoints', 'exit', 'carveReality', 'none'}

def format_card_lines(card_lines):
    output = ""
    for card_line in card_lines:
        #if isinstance(card_line, collections.Sequence):
        #    card_line = itertools.chain(*card_line)

        output += " -> ".join(card.name for card in card_line) + "\n"

    return output

def format_card_line(card_line):
    return " -> ".join(card.name for card in card_line)

class CardLinesContainer:
    __slots__ = ("card_lines",)

    def __init__(self, card_lines):
        self.card_lines = card_lines

    def calc_all_total_damage_and_sort(self, meta_state, stance=None):
        for card_line in self.card_lines:
            card_line.calc_total_damage(meta_state, stance=stance)

        self.sort()

    def sort(self):
        self.card_lines.sort(key=lambda x: x.total_damage)

    def format_all_with_total_damage(self, meta_state, stance=None):
        self.calc_all_total_damage_and_sort(meta_state, stance=stance)
        return "\n".join(card_line.format_card_line_with_total_damage() for card_line in self.card_lines) + "\n"

class CardLine:
    __slots__ = ("cards", "total_damage")

    def __init__(self, cards=None):
        if cards is None:
            cards = []
        self.cards = tuple(cards)

    def add_card(self, card):
        self.cards.append(card)

    def calc_total_damage(self, meta_state, stance=None):
        if stance is None:
            stance = meta_state.starting_stance

        self.total_damage = 0

        for card in self.cards:
            self.total_damage += card.calc_damage(stance=stance, strength=meta_state.strength)
            stance = card.calc_new_stance(stance, enemy_attacking=meta_state.enemy_attacking)

    def format_card_line_with_total_damage(self):
        card_line_str = format_card_line(self.cards)
        return f"[{self.total_damage}] ({len(self.cards)}) {card_line_str}"

class CardLibrary:
    __slots__ = ("filename", "cards", "cards_by_name", "all_effects")

    def __init__(self, filename):
        self.filename = filename

        with open(self.filename, "r") as f:
            contents = f.read()
            card_library_dict = yaml.safe_load(contents)

        self.cards = [Card.from_dict(card_as_dict) for card_as_dict in card_library_dict]
        self.cards_by_name = {card.name.lower(): card for card in self.cards}
        self.all_effects = set()
        for card in self.cards:
            self.all_effects.add(card.effect)

        print(f"all_effects: {self.all_effects}")

STANCE_EFFECTS = ("wrath", "exit", "fearNoEvil")

class MetaState:
    __slots__ = ("starting_stance", "max_smites", "max_through_violences", "min_card_plays", "max_card_plays", "enemy_attacking", "strength")

    def __init__(self, starting_stance="exit", max_smites=3, max_through_violences=2, min_card_plays=2, max_card_plays=5, enemy_attacking=True, strength=0):
        self.starting_stance = starting_stance
        self.max_smites = max_smites
        self.max_through_violences = max_through_violences
        self.min_card_plays = min_card_plays
        self.max_card_plays = max_card_plays
        self.enemy_attacking = enemy_attacking
        self.strength = strength

class Deck:
    __slots__ = ("library", "cards", "cards_by_name", "cards_by_effect")

    def __init__(self, library, card_names):
        self.library = library
        self.cards = []

        for card_name in card_names:
            card = library.cards_by_name.get(card_name.lower())
            if card is None:
                continue

            self.cards.append(card)

        self.cards_by_name = {card.name.lower(): card for card in self.cards}
        self.cards_by_effect = collections.defaultdict(list)
        for card in self.cards:
            self.cards_by_effect[card.effect].append(card)

    def _add_cards_with_effects_to_card_effect_partition(self, card_effect_partition, effect_names_for_partition_group, card_effect_partition_key):
        #if card_effect_partition_key is None:
        #    card_effect_partition_key = ",".join(effect_names_for_partition_group)

        for effect_name_for_partition_group in effect_names_for_partition_group:
            card_effect_partition[card_effect_partition_key].extend(self.cards_by_effect[effect_name_for_partition_group])

    def partition_by_effect(self, *effect_partition_format, other_key="other"):
        card_effect_partition = collections.defaultdict(list)
        used_partition_effects = set()

        for effect_partition_format_part in effect_partition_format:
            card_effect_partition_key, effect_names_for_partition_group = effect_partition_format_part
            self._add_cards_with_effects_to_card_effect_partition(card_effect_partition, effect_names_for_partition_group, card_effect_partition_key)
            used_partition_effects.update(effect_names_for_partition_group)

        unused_partition_effects = self.library.all_effects - used_partition_effects

        self._add_cards_with_effects_to_card_effect_partition(card_effect_partition, unused_partition_effects, other_key)

        return card_effect_partition

    def partition__stance__end_turn__non_stance_cards(self):
        return self.partition_by_effect(("stance", STANCE_EFFECTS), ("endTurn", ("endTurn",)), other_key="nonStance")

    @classmethod
    def from_filenames(cls, library_filename, deck_filename):
        library = CardLibrary(library_filename)
        with open(deck_filename, "r") as f:
            card_names = [line.strip() for line in f if line.strip() != ""]

        return cls(library, card_names)

    # something about number of splits
    # e.g. in sample deck, has one "split" because one wrath source
    # but maybe for divinity, prioritize stance changing last
    # possible lines (for divinity):
    # - nonstance -> calm -> wrath -> exit -> endTurn
    # - nonstance -> calm -> wrath -> endTurn
    # - nonstance -> calm -> exit -> wrath -> endTurn
    # - nonstance -> wrath -> calm -> exit -> endTurn
    # - nonstance -> wrath -> exit -> calm -> endTurn
    # probably others
    # annoying thing: wrath -> calm -> wrath -> calm not the same as wrath -> wrath -> calm -> calm

    def gen_unique_card_lines_for_effect(self, cards_with_effect, meta_state):
        unique_card_lines_for_effect = []

        for i in range(1, meta_state.max_card_plays + 1):
            cur_unique_card_lines_for_effect_dict = {tuple(card.name for card in card_line): card_line for card_line in itertools.combinations(cards_with_effect, i)}

            unique_card_lines_for_effect.extend(cur_unique_card_lines_for_effect_dict.values())

        return unique_card_lines_for_effect

    def calculate_lines_from_effect_order(self, effect_partition, effect_order, meta_state):
        all_effect_card_lines = []
        output = ""

        for effect in effect_order:
            cards_with_effect = effect_partition.get(effect)
            if cards_with_effect is None or len(cards_with_effect) == 0:
                continue

            effect_card_lines = self.gen_unique_card_lines_for_effect(cards_with_effect, meta_state)
            all_effect_card_lines.append(effect_card_lines)
            #output += f"== {effect} ==\n"
            #output += Deck.format_card_lines(effect_card_lines) + "\n"

        card_lines_container = CardLinesContainer([CardLine(itertools.chain.from_iterable(card_line) if isinstance(card_line, collections.Sequence) else card_line) for card_line in tuple(itertools.product(*all_effect_card_lines))])
        output += card_lines_container.format_all_with_total_damage(meta_state)
        #for card_line in card_lines:
        #    output += f"{card_line.format_card_line_with_total_damage
        #print(len(product_something))
        #print(product_something[0])
        #output += Deck.format_card_lines(card_lines) + "\n"
        return output

    def gen_damage_calcs(self, meta_state):
        if meta_state.starting_stance != "divinity":
            raise RuntimeError("Only divinity as starting stance is supported.")

        if meta_state.enemy_attacking:
            stance_end_turn_non_stance_partition = self.partition_by_effect(
                ("calm", ("fearNoEvil",)),
                ("wrath", ("wrath",)),
                ("exit", ("exit",)),
                ("endTurn", ("endTurn",)),
                other_key="nonStance"
            )
        else:
            stance_end_turn_non_stance_partition = self.partition_by_effect(
                ("wrath", ("wrath",)),
                ("exit", ("exit",)),
                ("endTurn", ("endTurn",)),
                other_key="nonStance"
            )

        #card_lines = []

        print(f"stance_end_turn_non_stance_partition: {stance_end_turn_non_stance_partition}")
        output = ""
        output += self.calculate_lines_from_effect_order(stance_end_turn_non_stance_partition, ("nonStance", "calm", "exit", "wrath", "endTurn"), meta_state)

        #unique_nonstance_card_lines = self.gen_unique_card_lines_for_effect(stance_end_turn_non_stance_partition["nonStance"], meta_state)
        #output += Deck.format_card_lines(unique_nonstance_card_lines)
            
        #for i in range(meta_state.min_card_plays, meta_state.max_card_plays + 1):
        #    unique_card_line_card_names_for_cur_num_card_plays = set()
        #
        #    for card_line in itertools.combinations(stance_end_turn_non_stance_partition["nonStance"], i):
        #        card_line_card_names = tuple(card.name for card in card_line)
        #        if card_line_card_names not in unique_card_line_card_names_for_cur_num_card_plays:
        #            output += " -> ".join(card_line_card_names) + "\n"
        #            unique_card_line_card_names_for_cur_num_card_plays.add(card_line_card_names)

        with open("gen_damage_calcs_combinations_test_out.dump", "w+") as f:
            f.write(output)

    def print_num_permutations(self, r=None):
        print(f"len(self.cards): {len(self.cards)}")
        print(f"num_permutations: {len(tuple(itertools.permutations(self.cards, r)))}")

#class Effect(Enum):
#    CALM = 0
#    CALM_ATTACKING = auto()
#    WRATH = auto()
#    EXIT = auto()
#    CRUSH = auto()
#    CARVE = auto()
#    END_TURN = auto()

# battle hymn, carve reality -> max smite
# reach heaven -> max through violence
