import polib
import sys

def remove_existing(reference_pot_path, input_pot_path, output_pot_path):
    reference_pot = polib.pofile(reference_pot_path)
    reference_msgids = set(entry.msgid for entry in reference_pot)

    input_pot = polib.pofile(input_pot_path)

    # filter out entries whose msgid exists in reference
    filtered_entries = [entry for entry in input_pot if entry.msgid not in reference_msgids]

    # create new POT file with filtered entries
    output_pot = polib.POFile()
    output_pot.metadata = input_pot.metadata
    output_pot.extend(filtered_entries)

    output_pot.save(output_pot_path)
    print(f"Filtered POT saved to: {output_pot_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: python unique.py reference.pot input.pot output.pot")
        sys.exit(1)

    reference_pot_path = sys.argv[1]
    input_pot_path = sys.argv[2]
    if len(sys.argv) == 3:
        output_pot_path = sys.argv[2]

    remove_existing(reference_pot_path, input_pot_path, output_pot_path)
