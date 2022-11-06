# report.py

from glob import glob
import shelve
from sys import argv

SHELVED_FILES = [
    'frontier.shelve',
    'tokens.shelve',
    'word_count.shelve',
    'subdomains.shelve'
]

def _shelve_file_exists(file: str) -> bool:
    return len(glob(file + '*')) > 0

def generate_report() -> None:
    # Part 1 - Number of Unique Visits
    print("Part 1: ", end="")
    if _shelve_file_exists(SHELVED_FILES[0]):
        frontier = shelve.open(SHELVED_FILES[0])
        print(f"VISITED {len(frontier)} UNIQUE SITES")
    else:
        print("FRONTIER NOT FOUND")

    print("Part 2: ", end="")
    if _shelve_file_exists(SHELVED_FILES[1]):
        word_count = shelve.open(SHELVED_FILES[1])
        max_words = max(word_count.values(), key=lambda p: p[1])
        print(f"Site with Highest Word Count: {max_words[0]} | {max_words[1]} words")
    else:
        print("WORD_COUNT NOT FOUND")
    
    print("Part 3: ", end="")
    if _shelve_file_exists(SHELVED_FILES[2]):
        tokens = shelve.open(SHELVED_FILES[2])
        top_tokens = sorted(tokens.items(), key=lambda w: (-w[1], w[0]))[:50]
        print(
            '\n' +
            [
                f"{word}\t{count}" for word, count in top_tokens
            ].join('\n')
        )
    else:
        print("TOKENS NOT FOUND")

    print("Part 4: ", end="")
    if _shelve_file_exists(SHELVED_FILES[3]):
        subdomains = shelve.open(SHELVED_FILES[3])
        max_subdomain = max(subdomains.values(), key=lambda p: p[1])
        print(f"Most common subdomain: {max_subdomain[0]} | {max_subdomain[1]} times")
    else:
        print("SUBDOMAINS NOT FOUND")

    return

def main(*argv) -> None:
    generate_report()

if __name__ == "__main__":
    main(*argv)