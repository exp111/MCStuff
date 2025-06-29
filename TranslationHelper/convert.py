import argparse
from io import TextIOWrapper
import json
import re

traitRegex = "([\t ]*[A-Z\u00C0-\u017F]+\.)+"
cardNumberRegex = "^([A-Z]\s*)+\s+\(\d+\/\d+\).*$"
numberRegex = "^(\d\s*)+$"
cardTypes = ["ANHANG", "VERRAT", "SCHERGE", "NEBENPLAN", "HAUPTPLAN", "UMGEBUNG", "VERBÜNDETER", "SCHURKE"]
stats = ["ANG", "WID", "PLA"]

parser = argparse.ArgumentParser(
                    prog='MC Translation Converter')
parser.add_argument(dest="input",default="in.txt", help="The name of the file")
args = parser.parse_args()
filename = args.input

content = []
with open(filename, encoding="utf-8") as f:
    content = f.readlines()

def sanitizeInput(lines: list[str]):
    out = []
    for line in lines:
        # type
        if line.strip() in cardTypes:
            continue
        # stats
        if line.strip() in stats:
            continue
        # card number
        if re.match(cardNumberRegex, line):
            continue
        # ignore lines that are just numbers
        if re.match(numberRegex, line):
            continue
        # artist credit
        if "©" in line or "@" in line or "FFG" in line:
            continue
        out.append(line)
    return out

def replaceSpecialIcons(text: str):
    return text.replace("*", "[star]")

def parseCard(text: list[str]):
    index = 0
    textEndIndex = len(text)
    # get title
    ## remove any whitespace or unique symbols. then convert to title-case 
    title = text[index].strip("+ \n").title()
    index += 1
    # get traits, if exist
    traits = ""
    ## check for trait regex (TRAIT. TRAIT.)
    for i in range(index, textEndIndex):
        if re.match(traitRegex, text[i]):
            print(f"Found traits at {i}, skipping {i - index} lines")
            # convert all traits to title-case, then rejoin into trait format
            allTraits = text[i].split(".")
            traits = str.join(". ", [t.strip().title() for t in allTraits]).strip()
            index = i + 1
    # check if there is a boost
    boost = ""
    ## check for a line that starts with boost start
    for i in range(index, textEndIndex):
        if text[i].startswith("* Boost:"):
            print("Found boost")
            boost = str.join("", text[i:textEndIndex]).replace("* Boost:", "<hr/>\n* <b>Boost</b>:").strip()
            textEndIndex = i
            break
    #TODO: flavor text

    # rest is text
    cardText = str.join("", text[index:textEndIndex]).strip()

    print(f"Title: {title}")
    print(f"Traits: {traits}")
    print(f"Text: {cardText.replace("\n", "\\n")}")
    print(f"Boost: {boost.replace("\n", "\\n")}")
    return {
        "title": title,
        "traits": traits,
        "text": replaceSpecialIcons(cardText),
        "boost": replaceSpecialIcons(boost)
    }

def writeCard(card, file: TextIOWrapper):
    obj = {
        "code": "ADD CODE",
        "name": card["title"],
        "text": card["text"]
    }
    if card["boost"]:
        obj["text"] += "\n" + card["boost"]
    if card["traits"]:
        obj["traits"] = card["traits"]
    file.write(json.dumps(obj, indent="\t", ensure_ascii=False))

texts = []
lines = []
print(content)
sanitized = sanitizeInput(content)
print(f"removed {len(sanitized) - len(content)} lines ({len(sanitized)}/{len(content)})")
for text in sanitized:
    if len(text.strip()) == 0:
        print("found end")
        print(lines)
        if len(lines) > 0:
            texts.append(lines)
            lines = []
        continue
    lines.append(text)
if len(lines) > 0:
    texts.append(lines)
print(texts)
print(f"found {len(texts)} parts")

cards = []
for text in texts:
    cards.append(parseCard(text))

with open("out_" + filename, "w", encoding="utf-8") as f:
    for card in cards:
        writeCard(card, f)
        f.write(",\n")
