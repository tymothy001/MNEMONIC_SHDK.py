import hashlib
import hmac
import struct
import sys
from mnemonic import Mnemonic
from bip32utils import BIP32Key
def print_logo():
    logo = """
___    ___     ___     _________     ___        __                    ___    __
\ /    \ /     \ /    |/  | |  \|    \  \      / /         /\         \  \   \/
| |    | |     | |        | |        |\  \    // |        /. \        ||\ \  ||
| |____| |     | |        | |        ||\  \  //| |       // \ \       || \ \ ||
| |    | |     | |        | |        || \  \// | |      //___\ \      ||  \ \||
| |    | |     | |        | |        ||  \  /  | |     //     \ \     ||   \  |
/_\    /_\     /_\        /_\       /_\   \/   /_\    /_\     /__\   /__\   \_|

                                    /|
                                    \\  \`.
    _      _   _   _           ,'/  ||   ) `.                _        _
   |_) |  / \ / \ | \        ,' (   //,-'_,-'    ,   |\  /| / \ |\ | |_ \ /
   |_) |_ \_/ \_/ |_/  .    `-._`-.  |  (_____,-'/   | \/ | \_/ | \| |_  |
                       \`-._____)  | | ,-'-.    /
                        \    ,-'-. | |/     ) ,'
                         `. (     \|     _,','
                           `.`._

====================================================================================
  MNEMONIC SCANER HD KEY V.O1

  The code automatically generates Bitcoin addresses from mnemonics,
  compares them with loaded address patterns,
  and saves the matching results to a file. Additionally, the script is equipped
  with a progress bar updated in the console,
  which visualizes the process of processing mnemonics, enhancing user interaction.

  usage: python3 MNEMONIC_SHDK.py

====================================================================================
    """
    print(logo)

if __name__ == '__main__':
    print_logo()

def mnem_to_seed(mnemonic):
    """Converts a mnemonic to a seed using PBKDF2."""
    passphrase = ""
    salt = "mnemonic" + passphrase
    seed = hashlib.pbkdf2_hmac('sha512', mnemonic.encode('utf-8'), salt.encode('utf-8'), 2048, dklen=64)
    return seed

def generate_addresses(mnemonic, num_addresses=10):
    """Generates a specified number of Bitcoin addresses from a given mnemonic."""
    seed = mnem_to_seed(mnemonic)
    bip32_root_key = BIP32Key.fromEntropy(seed)
    addresses = []
    for i in range(num_addresses):
        key = bip32_root_key.ChildKey(44 + 0x80000000) \
                             .ChildKey(0 + 0x80000000) \
                             .ChildKey(0 + 0x80000000) \
                             .ChildKey(0) \
                             .ChildKey(i)
        addresses.append(key.Address())
    return addresses

def load_patterns(filename):
    """Loads address patterns from a file."""
    with open(filename, 'r') as file:
        patterns = [line.strip() for line in file]
    return patterns

def compare_addresses(addresses, patterns):
    """Compares generated addresses against a list of patterns and returns matches.
    Patterns can be partial addresses (prefixes)."""
    matches = []
    for addr in addresses:
        for pattern in patterns:
            if addr.startswith(pattern):  # Check if the address starts with the pattern
                matches.append(addr)
    return matches

def save_matches_to_file(mnemonic, matches, filename):
    """Saves the mnemonic and matching addresses to a file."""
    with open(filename, 'a') as file:
        file.write(f'Mnemonic: {mnemonic}\n')
        for match in matches:
            file.write(f'Address: {match}\n')
        file.write('\n')  # Add an empty line for readability

def update_progress(current, total):
    """Updates the progress bar in the console."""
    progress_percentage = (current / total) * 100
    progress_bar_length = int(50 * (current / total))  # Width of the progress bar is 50 characters
    progress_bar = '#' * progress_bar_length + '-' * (50 - progress_bar_length)
    sys.stdout.write(f"\rProgress: [{progress_bar}] {progress_percentage:.2f}%")
    sys.stdout.flush()

if __name__ == '__main__':
    mnemonics_file = '12words.txt'
    patterns_file = 'w11.txt'
    output_file = 'f222.txt'
    patterns = load_patterns(patterns_file)
    total_found_addresses = 0

    with open(mnemonics_file, 'r') as file:
        mnemonics = [line.strip() for line in file if line.strip()]
        total_mnemonics = len(mnemonics)
        current_mnemonic = 0

        for mnemonic in mnemonics:
            current_mnemonic += 1
            addresses = generate_addresses(mnemonic)
            matches = compare_addresses(addresses, patterns)
            if matches:
                total_found_addresses += len(matches)
                save_matches_to_file(mnemonic, matches, output_file)
            update_progress(current_mnemonic, total_mnemonics)

    print("\nProcessing complete.")
    print(f"Total matching addresses found: {total_found_addresses}")
