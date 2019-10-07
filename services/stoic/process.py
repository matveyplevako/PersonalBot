from multiprocessing import Pool
import json
from time import sleep
from services.email.email_utils import upload_image_from_file
import os
from wand.image import Image
from wand.color import Color


def part1():
    '''
    Converts all pdf pages into img using wand and multiprocessing
    '''

    def convert_pdf(num):
        with Image(filename=f"pages/page{num}.pdf", resolution=400) as source:
            source.format = 'jpg'
            source.compression_quality = 100
            images = source.sequence
            img = Image(images[0])
            img.trim()
            img.background_color = Color("white")
            img.alpha_channel = 'remove'
            img.save(filename=f"images/{num}.png")

    with Pool(4) as p:
        p.map(convert_pdf, [i for i in range(366)])


def part2():
    '''
    Upload all images to imgur
    '''
    start = 0
    d = {}
    # To restart where we left
    if os.path.isfile("images.json"):
        with open("images.json") as file:
            d = json.load(file)
            start = int(max(d, key=int))
    for num in range(start, 366):
        print(num)
        link = upload_image_from_file(f"images/{num}.png")
        sleep(2.5)
        d[num] = link
        with open("images.json", "w") as out:
            json.dump(d, out)

# part1()
# part2()
