import math
import itertools

# insanity++: hoarder + insanity + specialized + allstar
# - scores: 350
# insanity*: hoarder + insanity + allstar
# - scores: 325
# insanity+: draft + insanity + specialized
# - scores: 300
# insanity: insanity
# - scores: 275

INSANITY_ONLY_SCORES = list(range(50, 325 + 1, 25))
INSANITY_DRAFT_SPECIALIZED_SCORE_300 = 350
BIGDECK_SCORES = list(range(450, 575 + 1, 25))

EMPTY_TUPLE = tuple()

class SeedCombination:
    __slots__ = ("bigdeck_scores", "insanity_scores")

    def __init__(self, bigdeck_scores=None, insanity_scores=None):
        if bigdeck_scores is None:
            bigdeck_scores = EMPTY_TUPLE
        if insanity_scores is None:
            insanity_scores = EMPTY_TUPLE

        self.bigdeck_scores = bigdeck_scores
        self.insanity_scores = insanity_scores

def ceil25(x):
    return math.ceil(x/25) * 25

def get_bigdeck_bigdeck_insanity_seed_combination_from_insanity_score(required_score, insanity_score):
   remaining_required_score = required_score - insanity_score * 2
   desired_bigdeck_score = ceil25(remaining_required_score)
   return SeedCombination(bigdeck_scores=(desired_bigdeck_score,), insanity_scores=(insanity_score, insanity_score))

def find_seed_combinations_for_unlock_1_score(unlock_1_score):
    required_score = ceil25(1000 + (750 - unlock_1_score))
    seed_combinations = []

    # check if we only need two bigdeck seeds
    largest_bigdeck_score = BIGDECK_SCORES[-1]
    if required_score - largest_bigdeck_score * 2 <= 0:
        desired_bigdeck_score = ceil25(required_score/2)
        seed_combination = SeedCombination(bigdeck_scores=(desired_bigdeck_score, desired_bigdeck_score))
        seed_combinations.append(seed_combination)
    # check if we can get away with (bigdeck, insanity, insanity)
    elif required_score - INSANITY_DRAFT_SPECIALIZED_SCORE_300 * 2 <= BIGDECK_SCORES[-1]:
        largest_insanity_score = INSANITY_ONLY_SCORES[-1]
        # check if we have to use insanity score 300 which requires draft and specialized
        if required_score - largest_insanity_score * 2 > BIGDECK_SCORES[-1]:
            # have to use insanity score 300
            seed_combination = get_bigdeck_bigdeck_insanity_seed_combination_from_insanity_score(required_score, INSANITY_DRAFT_SPECIALIZED_SCORE_300)
            seed_combinations.append(seed_combination)
        else:
            # find all combinations of (bigdeck, insanity, insanity)
            # this is in case some seeds are easier to type out than others
            for insanity_score in reversed(INSANITY_ONLY_SCORES):
                if largest_bigdeck_score + insanity_score * 2 < required_score:
                    break

                seed_combination = get_bigdeck_bigdeck_insanity_seed_combination_from_insanity_score(required_score, insanity_score)
                seed_combinations.append(seed_combination)
    # must use (bigdeck, bigdeck, insanity)
    else:
        for insanity_score in reversed(INSANITY_ONLY_SCORES):
            if largest_bigdeck_score * 2 + insanity_score < required_score:
                break

            remaining_required_score = required_score - insanity_score
            desired_bigdeck_score = ceil25(remaining_required_score/2)
            #if (desired_bigdeck_score * 2 + insanity_score) - 25 >= required_score:
            #    continue

            seed_combination = SeedCombination(bigdeck_scores=(desired_bigdeck_score, desired_bigdeck_score), insanity_scores=(insanity_score,))
            seed_combinations.append(seed_combination)

    output = ""
    for seed_combination in seed_combinations:
        seed_combination_str_parts = itertools.chain((f"bigdeck: {bigdeck_score}" for bigdeck_score in seed_combination.bigdeck_scores), (f"insanity: {insanity_score}" for insanity_score in seed_combination.insanity_scores))
        acquired_score = sum(itertools.chain(seed_combination.bigdeck_scores, seed_combination.insanity_scores))
        output += f"[{acquired_score}]: " + ", ".join(seed_combination_str_parts) + "\n"

    return output

def main():
    output = ""

    for unlock_1_score in (375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625, 650, 675, 700, 725):
        required_score = ceil25(1000 + (750 - unlock_1_score))
        unlock_total_score = unlock_1_score + 300

        output += f"== {unlock_total_score}~{unlock_total_score+24} (total required score {required_score}) ==\n"
        output += find_seed_combinations_for_unlock_1_score(unlock_1_score)
        output += "\n"

    with open("find_defect_unlock_seeds_out.dump", "w+") as f:
        f.write(output)

if __name__ == "__main__":
    main()
