import requests, os
from rich.progress import track

BASE_URL = "https://marvelcdb.com/"
API_URL = "https://marvelcdb.com/api/public/cards/"
OUT = "../images"
IMG_KEY = "imagesrc"

cards_res = requests.get(API_URL)
cards = cards_res.json()

if not os.path.exists(OUT):
    os.mkdir(OUT)

# download files
print(f"Found {len(cards)} cards with {len([c for c in cards if IMG_KEY in c])} images.")
count = 0
for card in track(cards, description="Downloading..."):
    # skip if no img
    if not IMG_KEY in card:
        continue
    file_name = card['code'] + ".png"
    img_url = BASE_URL + card[IMG_KEY]
    path = os.path.join(OUT, file_name)
    # dont redownload
    if os.path.exists(path):
        continue
    # fetch + write to file
    r = requests.get(img_url)
    with open(path, "wb") as f:
        f.write(r.content)
        count = count + 1
print(f"Done. Downloaded {count} images.")
