import argparse
import html
import json
import os
import textwrap
from schema import Card, DeckOption, DeckRequirement

def directory(raw_path: str):
    raw_path = raw_path.replace("\"", "").replace("'", "").strip()
    if not os.path.isdir(raw_path):
        raise argparse.ArgumentTypeError('"{}" is not an existing directory'.format(raw_path))
    return os.path.abspath(raw_path)

parser = argparse.ArgumentParser(
                    prog='Marvel Champions Reprint List',
                    description='Checks the Marvel Champions JSON Repo for reprints')
parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output") # flag
parser.add_argument("-i", "--input", nargs="?", default=os.path.curdir, type=directory, help="The directory of the repo. Defaults to the current path.")
parser.add_argument("-o", "--output", nargs="?", default=os.path.curdir, type=directory, help="The directory where the output is writtent to. Defaults to the current path.")
args = parser.parse_args()
# args
verbose = args.verbose
inputDir = args.input
outputDir = args.output

def vprint(text: str):
    if verbose:
        print(text)

def write(text: str = "", out=None):
    print(text, file=out)
    vprint(text)

vprint("Args:")
vprint(args)

# consts
baseDir = inputDir
packSubDir = "pack"
packsFile = "packs.json"
dbUrl = "https://marvelcdb.com/card/{0}"

vprint("Reading files")
# TODO: sanity check the input dir

# get all existing original files
packs = {}
for entry in os.scandir(os.path.join(baseDir, packSubDir)):
    if entry.is_file() and entry.name.endswith("json"):
        with open(entry.path, mode="r", encoding="utf-8") as f:
            packs[entry.name] = json.load(f)
#print(packs)

# check if any files were found
if len(packs) == 0:
    print("No files found.")
    exit(0)

vprint(f"{len(packs)} files loaded.")

# map into cards list
cards: list[Card] = []
for pack in packs.values():
    cards = cards + pack

def getCardUrl(card: Card):
    return dbUrl.format(card.get("code"))

def getCardByCode(code: str):
    return next(filter(lambda c: c.get("code") == code, cards)) or None

def isReprint(card: Card):
    isDuplicate = card.get("duplicate_of") is not None
    if not isDuplicate:
        return False
    orig = card.get("duplicate_of")
    card = getCardByCode(orig)
    if card is None:
        print(f"Card with code {isDuplicate} not found")
    return True

def isUniquePlayerCard(card: Card):
    # ignore hero, encounter and campaign cards
    if card.get("faction_code") in ["encounter", "hero", "campaign"]:
        return False
    code = card.get("code")
    # code doesnt exist OR card is duplicate
    if code is None or card.get("duplicate_of") is not None:
        return False
    duplicates = list(filter(lambda c: c.get("duplicate_of") == code, cards))
    if len(duplicates) > 0:
        return False
    return True

# list reprints (sorted by pack)
reprints: dict[str, list[Card]] = {}
# get reprints and sort by pack
for card in filter(isReprint, cards):
    pack = card.get("pack_code")
    if not pack in reprints:
        reprints[pack] = []
    reprints[pack].append(card)
# write
reprintOutputPath = os.path.join(outputDir, f"reprints.md")
with open(reprintOutputPath, "w", encoding="utf-8") as out:
    write("# Reprints", out)
    for pack in reprints:
        write(f"## {pack} ({len(reprints[pack])})", out)
        for card in reprints[pack]:
            orig = getCardByCode(card.get("duplicate_of"))
            write(f"- [{orig.get("name")}]({getCardUrl(orig)}) x{card.get("quantity")}", out)
# list unique cards with their corresponding packs (in full list and in nested list sorted by packs)
# get reprints and sort by pack
uniqueCards = list(filter(isUniquePlayerCard, cards))
uniqueOutputPath = os.path.join(outputDir, f"uniques.md")
with open(uniqueOutputPath, "w", encoding="utf-8") as out:
    write("# Unique Cards", out)
    write("## Sorted by Name", out)
    for card in sorted(uniqueCards, key=lambda c: c.get("name").strip("\"' ")):
        write(f"- [{card.get("name")}]({getCardUrl(card)}) x{card.get("quantity")} ({card.get("pack_code")})", out)

    write("", out)
    write("## Sorted by Pack", out)
    uniques: dict[str, list[Card]] = {}
    for card in uniqueCards:
        pack = card.get("pack_code")
        if not pack in uniques:
            uniques[pack] = []
        uniques[pack].append(card)
    for pack in uniques:
        write(f"### {pack} ({len(uniques[pack])})", out)
        for card in uniques[pack]:
            write(f"- [{card.get("name")}]({getCardUrl(card)}) x{card.get("quantity")}", out)