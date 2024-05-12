import hashlib
import hmac
import struct
import sys
import os
from multiprocessing import Pool
import psutil
import time
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes

def print_logo():
    logo = """
====================================================================================
  MNEMONIC SCANER HD KEY V.02 Zmodyfikowany MULTI

  The code automatically generates Bitcoin addresses from mnemonics,
  compares them with loaded address patterns,
  and saves the matching results to a file. Additionally, the script is equipped
  with a progress bar updated in the console,
  which visualizes the process of processing mnemonics, enhancing user interaction.

  usage: python3 MNEMONIC_SHDK_multi2.0.py

====================================================================================
    """
    print(logo)

def load_patterns(filename='patterns.txt'):
    """Loads a list of address patterns from a file."""
    with open(filename, 'r') as file:
        patterns = [line.strip() for line in file if line.strip()]
    return patterns

def generate_addresses(mnemonic):
    """Generates Bitcoin addresses from a mnemonic."""
    seed = Bip39SeedGenerator(mnemonic).Generate()
    bip44_mst = Bip44.FromSeed(seed, Bip44Coins.BITCOIN)
    addresses = []
    for idx in range(5):
        bip44_acc = bip44_mst.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT)
        bip44_addr = bip44_acc.AddressIndex(idx)
        addresses.append(bip44_addr.PublicKey().ToAddress())
    return addresses

def compare_addresses(addresses, patterns):
    """Compares a list of addresses with a list of patterns and returns matches."""
    matches = []
    for addr in addresses:
        for pattern in patterns:
            if addr.startswith(pattern):
                matches.append(addr)
    return matches

def process_mnemonic(mnemonic_data):
    mnemonic, patterns = mnemonic_data
    addresses = generate_addresses(mnemonic)
    matches = compare_addresses(addresses, patterns)
    return (mnemonic, matches)

def update_progress(current, total, start_time, found_addresses):
    """Updates the progress bar in the console with additional system stats, keeping the stats static."""
    elapsed_time = time.time() - start_time
    progress_percentage = (current / total) * 100
    remaining_time = (elapsed_time / current) * (total - current) if current > 0 else 0
    progress_bar_length = int(50 * progress_percentage / 100)
    progress_bar = '#' * progress_bar_length + '-' * (50 - progress_bar_length)
    cpu_usage = psutil.cpu_percent(interval=None)

    # Clear the current line and move cursor up 4 lines
    sys.stdout.write('\x1b[2K')
    sys.stdout.write('\x1b[4A')

    # Print the stats
    sys.stdout.write(f"\rProgress: [{progress_bar}] {progress_percentage:.2f}% Completed\n")
    sys.stdout.write(f"CPU Usage: {cpu_usage}%\n")
    sys.stdout.write(f"Estimated Time Remaining: {remaining_time:.2f} seconds\n")
    sys.stdout.write(f"Total Found Addresses: {found_addresses}\n")
    sys.stdout.flush()

def main():
    print_logo()
    patterns = load_patterns()
    with open('12words1.txt', 'r') as file:
        mnemonics = [line.strip() for line in file if line.strip()]
        total_mnemonics = len(mnemonics)

    start_time = time.time()
    total_found_addresses = 0
    results = []

    # Print placeholders for the stats
    print("\n" * 4)  # Ensure there are 4 lines for the stats

    with Pool(os.cpu_count()) as pool:
        for i, result in enumerate(pool.imap(process_mnemonic, [(mnemonic, patterns) for mnemonic in mnemonics])):
            results.append(result)
            if result[1]:  # Only if there are matches
                total_found_addresses += len(result[1])
            update_progress(i + 1, total_mnemonics, start_time, total_found_addresses)

    # Write results to file
    with open('FUNDS.txt', 'w') as f:
        for mnemonic, matches in results:
            if matches:
                f.write(f"Mnemonic: {mnemonic}\n")
                f.write("Matches:\n")
                for match in matches:
                    f.write(f"{match}\n")
                f.write("\n")

    # Clear and reset position after completion
    sys.stdout.write('\x1b[2K')
    sys.stdout.write('\x1b[4A')
    print("\nScan complete.")

if __name__ == '__main__':
    main()
