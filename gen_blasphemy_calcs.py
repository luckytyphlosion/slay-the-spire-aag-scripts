import damage_calc

def main():
    deck = damage_calc.Deck.from_filenames("card_library.yml", "sample_deck.dump")
    library = deck.library

    #deck.print_num_permutations()
    meta_state = damage_calc.MetaState(
        starting_stance="divinity"
    )
    deck.gen_damage_calcs(meta_state)

if __name__ == "__main__":
    main()
