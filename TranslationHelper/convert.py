import argparse
from io import TextIOWrapper
import json
import re

traitRegex = "([\t ]*[A-Z]+\.)+"

parser = argparse.ArgumentParser(
                    prog='MC Translation Converter')
parser.add_argument(dest="input",default="in.txt", help="The name of the file")
args = parser.parse_args()
filename = args.input

content = []
with open(filename, encoding="utf-8") as f:
    content = f.readlines()

def replaceSpecialIcons(text: str):
    return text.replace("*", "[star]")

def parseCard(content: list[str]):
    print(content)
    index = 0
    # get title
    ## remove any whitespace or unique symbols. then convert to title-case 
    title = content[index].strip("+ \n").title()
    index += 1
    # get traits, if exist
    traits = ""
    # check for regex (TRAIT. TRAIT.)
    if re.match(traitRegex, content[index]):
        print("Found traits")
        # convert all traits to title-case, then rejoin into trait format
        allTraits = content[index].split(".")
        traits = str.join(". ", [t.strip().title() for t in allTraits])
        index += 1
    # check if there is a boost
    boost = ""
    textEndIndex = len(content)
    #TODO: flavor text
    # check for a line that starts with boost start
    for i in range(index, textEndIndex):
        if content[i].startswith("* Boost:"):
            print("Found boost")
            boost = str.join("", content[i:textEndIndex]).replace("* Boost:", "<hr/>\n* <b>Boost</b>:")
            textEndIndex = i
            break

    # rest is text
    text = str.join("", content[index:textEndIndex]).strip()

    print(f"Title: {title}")
    print(f"Traits: {traits}")
    print(f"Text: {text.replace("\n", "\\n")}")
    print(f"Boost: {boost.replace("\n", "\\n")}")
    return {
        "title": title,
        "traits": traits,
        "text": replaceSpecialIcons(text),
        "boost": replaceSpecialIcons(boost)
    }

def writeCard(card, file: TextIOWrapper):
    obj = {
        "code": "ADD CODE",
        "name": card["title"],
        "text": card["text"] + "\n" + card["boost"]
    }
    if card["traits"]:
        obj["traits"] = card["traits"]
    file.write(json.dumps(obj, indent="\t", ensure_ascii=False))

card = parseCard(content)

with open("out.txt", "w", encoding="utf-8") as f:
    writeCard(card, f)
