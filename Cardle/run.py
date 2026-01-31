import argparse
import codecs
import html
import json
import os
import textwrap

import requests
from card_schema import Card, DeckOption, DeckRequirement
from pack_schema import Pack
import sys

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
parser.add_argument("-o", "--output", nargs="?", default=os.path.curdir, type=directory, help="The directory where the output is written to. Defaults to the current path.")
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
translationsSubDir = "translations"
packsFile = "packs.json"
lang = "de"
apiUrl = "https://marvelcdb.com/api/public/cards/"

vprint("Fetching data")
dbData = requests.get(apiUrl).json()

vprint("Reading files")
# TODO: sanity check the input dir

translationDir = ""
if lang is not None:
    translationDir = os.path.join(baseDir, translationsSubDir, lang)
    if not os.path.exists(translationDir):
        print(f"Can't find translations directory for lang {lang}.")
        sys.exit(1)

def loadPacks(path: str):
    packs = {}
    for entry in os.scandir(path):
        if entry.is_file() and entry.name.endswith("json"):
            with open(entry.path, mode="r", encoding="utf-8") as f:
                packs[entry.name] = json.load(f)
    return packs

def loadAllPacks(path: str):
    allPacks: list[Pack] = []
    with open(path, mode="r", encoding="utf-8") as f:
        allPacks = json.load(f)
    return allPacks

# get all existing original files
packs = loadPacks(os.path.join(baseDir, packSubDir))
vprint(f"{len(packs)} pack files loaded.")

translatedPacks = None
if lang is not None:
    translatedPacks = loadPacks(os.path.join(translationDir, packSubDir))
    vprint(f"{len(packs)} translation pack files loaded.")

# get packs
allPacks: list[Pack] = loadAllPacks(os.path.join(baseDir, packsFile))
vprint(f"{len(allPacks)} packs loaded.")

translatedAllPacks = None
if lang is not None:
    translatedAllPacks = loadAllPacks(os.path.join(translationDir, packsFile))
    vprint(f"{len(packs)} translation packs loaded.")

# check if any files were found
if len(packs) == 0:
    print("No files found.")
    exit(0)

# map into cards list
cards: list[Card] = []
for pack in packs.values():
    cards = cards + pack
vprint(f"Loaded {len(cards)} cards.")

translatedCards: list[Card] = []
if lang is not None:
    for pack in translatedPacks.values():
        translatedCards = translatedCards + pack
    vprint(f"Loaded {len(cards)} translated cards.")

def getTranslatedCardName(card: Card):
    c = list(filter(lambda c: c.get("code") == card.get("code"), translatedCards))
    if len(c) > 0:
        return c[0].get("name") or card.get("name")
    else:
        return ""
    
def getResources(card: Card):
    ret = []
    if card.get("resource_energy") is not None:
        ret = ret + (["e"] * card.get("resource_energy"))
    if card.get("resource_mental") is not None:
        ret = ret + (["m"] * card.get("resource_mental"))
    if card.get("resource_physical") is not None:
        ret = ret + (["p"] * card.get("resource_physical"))
    if card.get("resource_wild") is not None:
        ret = ret + (["w"] * card.get("resource_wild"))
    return ret

def hasUnmarkedDuplicate(c: Card):
    # ignore marked duplicate
    if c.get("duplicate_of") is not None:
        return None
    # check if any other card matches these parameters: name, cost, faction, type, subname. then its probably a reprint that isn't marked properly
    filtered = list(filter(lambda x: x.get("code") != c.get("code") and x.get("name") == c.get("name") and x.get("cost") == c.get("cost") and x.get("faction_code") == c.get("faction_code") and x.get("type_code") == c.get("type_code") and x.get("subname") == c.get("subname"), cards))
    return filtered[0] if len(filtered) > 0 else None

class OutputCard:
    code: str
    cost: str
    type: str
    faction: str
    name: str
    name_de: str
    resources: list[str]
    packs: list[str]
    sets: list[str]
    illustrators: list[str]
    traits: list[str]
    img: str

vprint("Sorting cards by code")
cards.sort(key=lambda x: x.get('code'))

vprint("Collecting output")
output: dict[str, OutputCard] = {}
duplicates: list[Card] = []
for card in cards:
    # skip encounter cards
    if card.get("faction_code") in ["encounter", "campaign"]:
        continue

    # skip identity cards
    if card.get("type_code") in ["hero", "alter_ego"]:
        continue

    # skip hidden cards (mostly used for backsides like 3 form heroes or campaign upgrades)
    if card.get("hidden"):
        continue

    # is reprint, add later to packs
    if card.get("duplicate_of") is not None:
        duplicates.append(card)
        continue

    # check for unmarked duplicates (ie in hero packs). add those as duplicates if the other card was already added
    cardDuplicate = hasUnmarkedDuplicate(card)
    if cardDuplicate is not None and cardDuplicate.get("code") in output:
        card["duplicate_of"] = cardDuplicate.get("code")
        print(f"Card is duplicate {card.get("name")} ({card.get("code")}) of {cardDuplicate.get("name")} ({cardDuplicate.get("code")})")
        duplicates.append(card)
        continue

    dbCard = list(filter(lambda x: x.get("code") == card.get("code"), dbData))
    if dbCard is None or len(dbCard) == 0:
        print(f"Card {card.get("code")} not found in DB data.")
        continue
    dbCard = dbCard[0]

    # create ouput
    output[card.get("code")] = {
        "code": card.get("code"),
        "cost": card.get("cost"),
        "type": card.get("type_code"),
        "faction": card.get("faction_code"),
        "name": card.get("name"),
        "name_de":  getTranslatedCardName(card),
        "resources": getResources(card),
        "packs": [card.get("pack_code")],
        "sets": [card.get("set_code")],
        # split by &, then strip whitespace
        "illustrators": list(map(lambda s: s.strip(), card.get("illustrator").split("&") if card.get("illustrator") is not None else [])),
        # split by ., then strip whitespace. as traits always end with . also remove empty strings afterwards
        # replaces shield so the trait isnt split up
        "traits": list(filter(lambda s: s.strip(), map(lambda s: s.strip(), card.get("traits").replace("S.H.I.E.L.D", "SHIELD").split(".") if card.get("traits") is not None else []))),
        "img": dbCard["imagesrc"] if dbCard and "imagesrc" in dbCard else None
    }

vprint("Adding reprints")
# add reprints to packs
for duplicate in duplicates:
    origCode = duplicate.get("duplicate_of")
    if origCode not in output:
        print(f"Missing card {origCode}")
        continue
    if duplicate.get("pack_code") not in output[origCode]["packs"]:
        output[origCode]["packs"].append(duplicate.get("pack_code"))
    if duplicate.get("set_code") not in output[origCode]["sets"]:
        output[origCode]["sets"].append(duplicate.get("set_code"))


vprint("Starting writing")
# write to file
fileName = "output.json"
outputPath = os.path.join(outputDir, fileName)
with open(outputPath, "w", encoding="utf-8") as out:
    write(json.dumps(list(output.values())), out)
vprint("Finished writing.")