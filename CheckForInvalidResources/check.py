import requests, os, sys
from PIL import Image

API_URL = "https://marvelcdb.com/api/public/cards/"
IMAGE_FOLDER = "../images"
KEY_RESOURCES = ["resource_energy", "resource_mental", "resource_physical", "resource_wild"]

COLORS = {
    "red": (255,0,0),
    "yellow": (255,255,0),
    "blue": (0,0,255),
    "green": (0,255,0)
}

RESOURCE_COLORS = {
    "resource_energy": "yellow",
    "resource_mental": "blue",
    "resource_physical": "red",
    "resource_wild": "green"
}

# gets closest color defined in COLORS
def closest_color(requested_colour):
    distances = {}
    for name in COLORS.keys():
        (r_c, g_c, b_c) = COLORS[name]
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        distances[name] = rd + gd + bd
    return min(distances, key=distances.get)

cards_res = requests.get(API_URL)
cards = cards_res.json()

for card in cards:
    file_name = card['code'] + ".png"
    path = os.path.join(IMAGE_FOLDER, file_name)
    # image not found
    if not os.path.exists(path):
        print(f"Image {file_name} not found")
        continue
    # card has no ressources
    resources = [k for k in KEY_RESOURCES if k in card]
    colors_count = sum([card[k] for k in resources])
    #INFO: this does only check if the json has the correct resource types, not the correct resource count. this means it will not detect if
    # - the json has no resource but the card has some
    # - the json has less resources than the card
    # - the json has more resources than the card (at least not reliably)
    if colors_count == 0:
        continue
    with Image.open(path) as img:
        # rotate sideways cards
        if img.width > img.height:
            img = img.rotate(angle=90, expand=True)
        # get resource colors from pixel positions
        pix = img.load()
        #TODO: this fails if the card has a scanned card border (ie ghost spider). can we trim it?
        w = round(img.width * 0.03)
        colors_pos = [(w, round(img.height * (0.95 - i * 0.05))) for i in range(colors_count)]
        colors_rgb = [pix[pos[0], pos[1]] for pos in colors_pos]
        colors = [closest_color(rgb) for rgb in colors_rgb]
        # check if img matches
        for resource in resources:
            color_count = len([c for c in colors if c == RESOURCE_COLORS[resource]])
            if color_count != card[resource]:
                print(f"Mismatch in card {card['name']} ({card['code']}), resource {resource}")
                print(f"Has {color_count}x {RESOURCE_COLORS[resource]}. Should have {card[resource]}")
                print("Pixel Position:")
                print(colors_pos)
                print("Pixel RGB:")
                print(colors_rgb)
                print("Nearest color:")
                print(colors)
                print()

