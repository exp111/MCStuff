import argparse
from io import TextIOWrapper
import json
import re

traitRegex = "([\t ]*[A-Z\u00C0-\u017F]+\.)+"

parser = argparse.ArgumentParser(
                    prog='MC Translation Converter')
parser.add_argument(dest="input",default="in.txt", help="The name of the file")
args = parser.parse_args()
filename = args.input

content = []
with open(filename, encoding="utf-8") as f:
    content = f.readlines()

def replaceSpecialIcons(text: str):
    return text.replace("*", "[star]").replace("•", "\u2022")

def parseCard(text: list[str]):
    index = 0
    # get title
    ## remove any whitespace or unique symbols. then convert to title-case 
    title = text[index].strip("+ \n").title()
    index += 1
    # get traits, if exist
    traits = ""
    # check for regex (TRAIT. TRAIT.)
    if re.match(traitRegex, text[index]):
        print("Found traits")
        # convert all traits to title-case, then rejoin into trait format
        allTraits = text[index].split(".")
        traits = str.join(". ", [t.strip().title() for t in allTraits]).strip()
        index += 1
    # check if there is a boost
    boost = ""
    textEndIndex = len(text)
    #TODO: flavor text
    # check for a line that starts with boost start
    for i in range(index, textEndIndex):
        if text[i].startswith("* Boost:"):
            print("Found boost")
            boost = str.join("", text[i:textEndIndex]).replace("* Boost:", "<hr/>\n* <b>Boost</b>:").strip()
            textEndIndex = i
            break

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
for text in content:
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
