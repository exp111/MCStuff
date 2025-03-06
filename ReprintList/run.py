import argparse
import html
import json
import os
import textwrap
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
parser.add_argument("-l", "--lang", default=None, help="The language code")
parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output") # flag
parser.add_argument("-i", "--input", nargs="?", default=os.path.curdir, type=directory, help="The directory of the repo. Defaults to the current path.")
parser.add_argument("-o", "--output", nargs="?", default=os.path.curdir, type=directory, help="The directory where the output is writtent to. Defaults to the current path.")
args = parser.parse_args()
# args
lang = args.lang.strip() if args.lang is not None else None
verbose = args.verbose
inputDir = args.input
outputDir = args.output

def vprint(text: str):
    if verbose:
        print(text)

def write(text: str = "", out=None):
    print(text, file=out)
    vprint(text)

def writeSpoilerStart(summary: str = "", out=None):
    print("<details>", file=out)
    print(f"<summary>{summary}</summary>", file=out)
    # empty line needed
    print("", file=out)
    vprint(f"Spoiler Start {summary}")

def writeSpoilerEnd(out=None):
    print("</details>", file=out)
    vprint(f"Spoiler End")

vprint("Args:")
vprint(args)

# consts
baseDir = inputDir
packSubDir = "pack"
translationsSubDir = "translations"
packsFile = "packs.json"
dbUrl = "https://marvelcdb.com/card/{0}"

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

def getPackName(packCode: str):
    if lang is not None:
        pack = list(filter(lambda p: p.get("code") == packCode, translatedAllPacks))
        if len(pack) > 0:
            return pack[0].get("name") or packCode
    pack = list(filter(lambda p: p.get("code") == packCode, allPacks))
    if len(pack) > 0:
        return pack[0].get("name") or packCode
    else:
        return packCode
    
def getCardName(card: Card):
    if lang is not None and card.get("pack_code") is not None:
        c = list(filter(lambda c: c.get("code") == card.get("code"), [x for xs in translatedPacks.values() for x in xs]))
        if len(c) > 0:
            return c[0].get("name") or card.get("name")
    return card.get("name")

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
        writeSpoilerStart(f"## {getPackName(pack)} ({len(reprints[pack])})", out)
        for card in reprints[pack]:
            orig = getCardByCode(card.get("duplicate_of"))
            write(f"- [{getCardName(orig)}]({getCardUrl(orig)}) x{card.get("quantity")}", out)
        writeSpoilerEnd(out)
# list unique cards with their corresponding packs (in full list and in nested list sorted by packs)
# get reprints and sort by pack
uniqueCards = list(filter(isUniquePlayerCard, cards))
outputFileName = "uniques.md" if lang is None else f"uniques_{lang}.md"
uniqueOutputPath = os.path.join(outputDir, outputFileName)
with open(uniqueOutputPath, "w", encoding="utf-8") as out:
    write("# Unique Cards", out)
    write("## Sorted by Name", out)
    writeSpoilerStart("Spoiler", out)
    for card in sorted(uniqueCards, key=lambda c: getCardName(c).strip("\"' ")):
        write(f"- [{getCardName(card)}]({getCardUrl(card)}) x{card.get("quantity")} ({getPackName(card.get("pack_code"))})", out)
    writeSpoilerEnd(out)

    # new line
    write(out=out)
    write("## Sorted by Pack", out)
    writeSpoilerStart("Spoiler", out)
    uniques: dict[str, list[Card]] = {pack.get("code"): [] for pack in allPacks}
    # map cards by pack
    for card in uniqueCards:
        pack = card.get("pack_code")
        if not pack in uniques:
            uniques[pack] = []
        uniques[pack].append(card)
    for pack in allPacks:
        code = pack.get("code")
        write(f"### {getPackName(code)} ({len(uniques[code])})", out)
        for card in uniques[code]:
            write(f"- [{getCardName(card)}]({getCardUrl(card)}) x{card.get("quantity")}", out)
    writeSpoilerEnd(out)