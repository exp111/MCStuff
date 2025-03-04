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
packSubDir = "pack"
packsFile = "packs.json"

vprint("Reading files")
# check if the folder structure is somewhat right

# get all existing original files
for entry in os.scandir(os.path.join(baseDir, packSubDir)):
    packFiles = []

# check if any files were found
if len(queue) == 0:
    print("No files found.")
    exit(0)

missingFiles: list[str] = []
missingInfos: list[MissingInfo] = []

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