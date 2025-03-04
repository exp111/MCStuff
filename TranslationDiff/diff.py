import argparse
import html
import json
import os
import textwrap

def directory(raw_path: str):
    raw_path = raw_path.replace("\"", "").replace("'", "").strip()
    if not os.path.isdir(raw_path):
        raise argparse.ArgumentTypeError('"{}" is not an existing directory'.format(raw_path))
    return os.path.abspath(raw_path)

parser = argparse.ArgumentParser(
                    prog='Marvel Champions Translation Diff',
                    description='Checks the Marvel Champions JSON Repo for missing translations')
parser.add_argument("-l", "--lang", default="de", help="The language code for the translation")
parser.add_argument("-a", "--attributes", action="store_true", help="If used also compares the object keys for equalness. May lead to false positives as values may be the same in the two languages.") # flag
parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output") # flag
parser.add_argument("-i", "--input", nargs="?", default=os.path.curdir, type=directory, help="The directory of the repo. Defaults to the current path.")
parser.add_argument("-o", "--output", nargs="?", default=os.path.curdir, type=directory, help="The directory where the output is writtent to. Defaults to the current path.")
args = parser.parse_args()
# args
lang = args.lang
listAttributes = args.attributes
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
translationBaseDir = "translations"
packSubDir = "pack"

# whitelisted files. are not checked
whitelist = ["package.json", "settypes.json"]
attributes = ["flavor", "text"] # "name", "traits" not included

class MissingInfoEntry:
    code: str
    name: str

    def __init__(self, code, name):
        self.code = code
        self.name = name

class MissingInfoAttribute:
    code: str
    attribute: str
    value: str

    def __init__(self, code, attribute, value):
        self.code = code
        self.attribute = attribute
        self.value = value

class MissingInfo:
    file: str
    entries: list[MissingInfoEntry]
    attributes: list[MissingInfoAttribute]

    def __init__(self, name):
        self.file = name
        self.entries = []
        self.attributes = []


# for each json in basedir and packSubDir:
#   check if file exists in translationDir:
#   if no: 
#       mark as missing
#   else: 
#       check object keys + values for diff (whitelist keys per file):
#       if different:
#           -- do nothing as it was changed. maybe check if german language
#       if not different:
#           mark as missing
queue = []
def isValid(entry: os.DirEntry):
    return entry.is_file() and entry.name.endswith(".json") and entry.name not in whitelist

vprint("Checking original files")
# check if the folder structure is somewhat right
if not os.path.exists(os.path.join(baseDir, translationBaseDir)):
    print("No translations directory was found. Did you select the right directory?")
    exit(1)

# get all existing original files
for entry in os.scandir(baseDir):
    # if the entry is the pack dir, add all valid files in there to the queue
    if entry.is_dir() and entry.name == packSubDir:
        for entry2 in os.scandir(entry.path):
            if isValid(entry2):
                queue.append(entry2)
    # and all top level valid files
    if isValid(entry):
        queue.append(entry)

# check if any files were found
if len(queue) == 0:
    print("No files found.")
    exit(0)

missingFiles: list[str] = []
missingInfos: list[MissingInfo] = []

# checks the attribute on the original and translated object and returns true/false depending on if the attrib has been translated
def checkAttrib(orig, trans, attrib):
    if attrib in orig:
        if attrib in trans:
            oVal = orig[attrib]
            tVal = trans[attrib]
            if oVal == tVal:
                # value the same => not translated?
                return False
            else:
                # value different => (probably) translated
                return True
        else:
            # missing key??
            return False
    # key not found, so ignore
    return True

vprint(f"{len(queue)} files found. Now checking if translated files for lang \"{lang}\" exist.")
for entry in queue:
    relPath = os.path.relpath(entry.path, baseDir)
    langPath = os.path.join(baseDir, translationBaseDir, lang, relPath)
    if not os.path.exists(langPath):
        # file is missing completely
        missingFiles.append(entry.name)
    else:
        info = MissingInfo(entry.name)
        # read both files
        with open(entry.path, "r", encoding="utf-8") as file:
            original = json.load(file)
        with open(langPath, "r", encoding="utf-8") as file:
            translation = json.load(file)
        # iterate through original file and check 
        for obj in original:
            # we dont need to translate duplicates
            if "duplicate_of" in obj:
                continue
            # find entry in translation
            result = next((t for t in translation if t["code"] == obj["code"]), None)
            if not result:
                # missing entry (not translated)
                info.entries.append(MissingInfoEntry(obj["code"], obj["name"]))
            else:
                if listAttributes:
                    for a in attributes:
                        if not checkAttrib(obj, result, a):
                            info.attributes.append(MissingInfoAttribute(obj["code"], a, obj[a]))
        # only add if something was found
        if len(info.attributes) > 0 or len(info.entries) > 0:
            missingInfos.append(info)

outputPath = os.path.join(outputDir, f"output_{lang}.md")
vprint(f"Writing {len(missingFiles)} + {len(missingInfos)} entries to output file:")
vprint(outputPath)
with open(outputPath, "w", encoding="utf-8") as out:
    write(f"Missing Files ({len(missingFiles)}):", out)
    for file in missingFiles:
        write(f"- {file}", out)
    
    write(f"Missing Entries ({len(missingInfos)}):", out)
    for info in missingInfos:
        # wrap in spoiler
        write("<details>", out)
        write(f"<summary>{info.file} ({len(info.entries) + len(info.attributes)})</summary>", out)
        write(out=out) # empty line needed
        for entry in info.entries:
            write(f"- Entry: {entry.code} ({html.escape(entry.name)})", out)
        for attrib in info.attributes:
            write(f"- Attribut: {attrib.code} ({attrib.attribute}, {textwrap.shorten(html.escape(attrib.value), width=100)})", out)
        write("</details>", out)