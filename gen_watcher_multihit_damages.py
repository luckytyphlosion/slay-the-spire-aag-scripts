
class MultihitAttack:
    __slots__ = ("damage", "num_hits")

    def __init__(self, damage, num_hits):
        self.damage = damage
        self.num_hits = num_hits

multihit_attacks = [
    MultihitAttack(4, 2),
    MultihitAttack(3, 3),
    MultihitAttack(6, 2),
    MultihitAttack(3, 4),
    MultihitAttack(5, 5),
    MultihitAttack(6, 6),
]

def main():
    output = ""
    START_BOOST = 2
    END_BOOST = 26

    for multihit_attack in multihit_attacks:
        output += "\t".join(f"{multihit_attack.damage + i}*{multihit_attack.num_hits} ({(multihit_attack.damage + i) * multihit_attack.num_hits})" for i in range(START_BOOST, END_BOOST + 1)) + "\n"

    output += "\n"
    output += "\t".join(f"Damage (+{i})" for i in range(START_BOOST, END_BOOST + 1)) + "\n"

    with open("gen_watcher_multihit_damages_out.dump", "w+") as f:
        f.write(output)


if __name__ == "__main__":
    main()
