import itertools
import collections
import json

MAX_CHAIN_LENGTH = 5
STANCES = ("Calm", "Wrath", "Exit")
STANCES_EXIT_FIRST = ("Exit", "Calm", "Wrath")
FLURRY_OF_BLOWS_DAMAGE = 4
GENERATE_VERBOSE_OUTPUT = False
COMBINE_UPGRADE_INFO = True

def main():
    output = ""
    stance_chains_by_unordered_stance_chain = {stance: collections.defaultdict(list) for stance in STANCES_EXIT_FIRST}

    for starting_stance in STANCES:
        #output += f"== Starting stance: {starting_stance} ==\n"
        for cur_chain_length in range(1, MAX_CHAIN_LENGTH + 1):
            for possible_chain in itertools.product(STANCES, repeat=cur_chain_length):
                #print(possible_chain)
                prev_stance = starting_stance
                is_valid_chain = True
                for stance in possible_chain:
                    if prev_stance == stance:
                        is_valid_chain = False
                        break

                    prev_stance = stance

                if is_valid_chain:
                    stance_chains_by_unordered_stance_chain[starting_stance][tuple(sorted(possible_chain))].append(possible_chain)
                    #output += " -> ".join(possible_chain) + "\n"

        #output += "\n"

    stance_chains_pruned = {stance: collections.defaultdict(list) for stance in STANCES}

    for starting_stance, stance_chain_by_unordered in stance_chains_by_unordered_stance_chain.items():
        output += f"== Starting stance: {starting_stance if starting_stance != 'Exit' else 'None'} ==\n"
        non_verbose_sorted_stance_output_by_damage_container = []

        for unordered_stance_chain, stance_chains in stance_chain_by_unordered.items():
            unordered_stance_chain_counter = collections.Counter()
            for stance in STANCES:
                unordered_stance_chain_counter[stance] = 0

            for stance in unordered_stance_chain:
                unordered_stance_chain_counter[stance] += 1

            unordered_stance_chain_parts = []
            damage = 0

            for stance, count in unordered_stance_chain_counter.items():
                if count > 0:
                    if count == 1:
                        unordered_stance_chain_parts.append(stance)
                    else:
                        unordered_stance_chain_parts.append(f"{stance} x{count}")

                    if stance == "Wrath":
                        damage += FLURRY_OF_BLOWS_DAMAGE * 2 * count
                    else:
                        damage += FLURRY_OF_BLOWS_DAMAGE * count

            unordered_stance_chain_parts.extend(("",) * (3 - len(unordered_stance_chain_parts)))

            if starting_stance == "Wrath":
                damage_if_in_hand = damage + FLURRY_OF_BLOWS_DAMAGE * 2
            else:
                damage_if_in_hand = damage + FLURRY_OF_BLOWS_DAMAGE

            if GENERATE_VERBOSE_OUTPUT:
                unordered_stance_chain_str = ", ".join(unordered_stance_chain_parts)
            else:
                unordered_stance_chain_str = " | ".join(f"{unordered_stance_chain_part: <8}" for unordered_stance_chain_part in unordered_stance_chain_parts)

            if GENERATE_VERBOSE_OUTPUT:
                output += f"=== {unordered_stance_chain_str} ({damage}; {damage_if_in_hand} if in hand) ===\n"
                for stance_chain in stance_chains:
                    output += " -> ".join(stance_chain) + "\n"

                output += "\n"
            else:
                if COMBINE_UPGRADE_INFO:
                    non_verbose_sorted_stance_output_by_damage_container.append((damage, f"{unordered_stance_chain_str} | {damage} ({damage * 3 // 2}); {damage_if_in_hand} ({damage_if_in_hand * 3 // 2}) if in hand\n"))                
                else:
                    non_verbose_sorted_stance_output_by_damage_container.append((damage, f"{unordered_stance_chain_str} | {damage}; {damage_if_in_hand} if in hand\n"))

        if not GENERATE_VERBOSE_OUTPUT:
            sorted_non_verbose_sorted_stance_output_by_damage_container_str = "".join(x[1] for x in sorted(non_verbose_sorted_stance_output_by_damage_container, key=lambda x: x[0]))
            output += sorted_non_verbose_sorted_stance_output_by_damage_container_str

        output += "\n"

    with open("generate_stance_chains_out.dump", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
