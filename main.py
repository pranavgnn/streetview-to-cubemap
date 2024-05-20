import itertools
import requests
from PIL import Image, ImageChops, ImageFilter
from streetview import search_panoramas
from io import BytesIO
from cubemap import equirectangular_to_cubemap
from threading import Thread
from time import sleep

zoom = 5
latitude, longitude = (13.3552696,74.7982442)

tile_width, tile_height = (512, 512)

# Hard coded for now, not happy about it :(
# TODO: Find out a mathematical function that satisfies given values
w_values = [0, 2, 4, 7, 13, 26]
h_values = [0, 1, 2, 4, 7, 13]
horizontal_clip = [0, 192, 384, 256, 0, 0]

def get_wh_from_zoom(zoom):
    return w_values[zoom], h_values[zoom]

def get_bytes(pano_id, zoom, x, y):

    return requests.get(
        f"https://cbk0.google.com/cbk?output=tile&panoid={pano_id}&zoom={zoom}&x={x}&y={y}"
    ).content

def paste_tile(output, pano_id, zoom, x, y):

    bytes = get_bytes(pano_id, zoom, x, y)
    img = Image.open(BytesIO(bytes))

    output.paste(img, (x * tile_width, y * tile_height))

def make_panorama(pano_id, zoom):

    width, height = get_wh_from_zoom(zoom)
    output = Image.new("RGB", (width * tile_width, height * tile_height), (255, 0, 0))
    threads = []

    # make tile-fetching threads
    for x, y in itertools.product(range(width), range(height)):
        thread = Thread(target=paste_tile, args=(output, pano_id, zoom, x, y))
        threads.append(thread)

    # start threads
    for t in threads:
        sleep(0.005)
        t.start()

    # yield for theads
    for t in threads:
        t.join()

    output.show()

    crop_start_x, crop_start_y, crop_end_x, crop_end_y = output.getbbox()

    ''' x repeat detection (works, but buggy. hence commented)

    found_repeat = False

    for i in range(tile_width):
        if found_repeat:
            break

        shifted_img = Image.new("RGB", (tile_width, crop_end_y))
        shifted_img.paste(output.crop((0, 0, tile_width, crop_end_y)), (i, 0))

        diff = ImageChops.difference(output.crop((crop_end_x - tile_width, 0, crop_end_x, crop_end_y)), shifted_img)
        # diff = diff.filter(ImageFilter.BLUR)
        # diff = diff.convert("1")
        diff.save(f"diffs/diff_{i}.jpg")

        if diff.getbbox()[2] < 0.9 * tile_width:
            crop_end_x -= tile_width - i
            found_repeat = True
            print(i)
            diff.show()
            break
            
    output.crop((0, 0, tile_width, crop_end_y)).save(f"diffs/_start.jpg")
    output.crop((crop_end_x - tile_width, 0, crop_end_x, crop_end_y)).save(f"diffs/_end.jpg")
    '''

    output = output.crop((crop_start_x, crop_start_y, crop_end_x - horizontal_clip[zoom], crop_end_y))
    output.save(f"{latitude},{longitude} zoom-{zoom}.png")
    # output.show()

    return output

# TODO: Rewrite search_panoramas instead of using the library due to unforseen edge-cases by the original author
panoids = search_panoramas(lat=latitude, lon=longitude)
panoid = panoids[0].pano_id

output = make_panorama(panoid, zoom)
equirectangular_to_cubemap(output, 256, latitude, longitude, zoom)

# https://jaxry.github.io/panorama-to-cubemap/
# https://matheowis.github.io/HDRI-to-CubeMap/