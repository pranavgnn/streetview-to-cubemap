import itertools
import requests
from PIL import Image, ImageChops
from streetview import search_panoramas
from io import BytesIO
from cubemap import equirectangular_to_cubemap

latitude, longitude = (51.500936,-0.1253679)

tile_width, tile_height = (512, 512)
w_values = [0, 2, 4, 7, 13, 26]
h_values = [0, 1, 2, 4, 7, 13]
horizontal_clip = [0, 192, 384, 256, 0, 0]

def get_wh_from_zoom(zoom):
    return w_values[zoom], h_values[zoom]

def get_bytes(pano_id, zoom, x, y):
    return requests.get(
        f"https://cbk0.google.com/cbk?output=tile&panoid={pano_id}&zoom={zoom}&x={x}&y={y}"
    ).content

def get_tiles(pano_id, zoom):
    width, height = get_wh_from_zoom(zoom)

    crop_width = width * tile_width - horizontal_clip[zoom]
    crop_height = 0

    output = Image.new("RGBA", (width * tile_width, height * tile_height), (255, 0, 0))

    # tiles = []

    for x, y in itertools.product(range(width), range(height)):
        bytes = get_bytes(pano_id, zoom, x, y)
        img = Image.open(BytesIO(bytes))
        img = img.convert("RGB")
        img_data = img.getdata()
        h = tile_height

        for i in range(0, tile_width * tile_height, tile_width):
                if img_data[i] == 0 or sum(img_data[i]) == 0:
                    h = i / tile_width
                    break

        if x == 0:
            crop_height += h

        output.paste(img, (x * tile_width, y * tile_height))
        # tiles.append(img)

    # for i in range(0, tile_width):
    #     shifted_img = Image.new("RGB", (tile_width, tile_height))
    #     shifted_img.paste(tiles[0], (i, 0))

    #     diff = ImageChops.difference(tiles[-height], shifted_img)
    #     diff.save(f"diffs/diff_{i}.jpg")

    # tiles[0].save(f"diffs/_start.jpg")
    # tiles[-height].save(f"diffs/_end.jpg")

    output = output.crop((0, 0, crop_width, crop_height))
    output.save(f"{latitude},{longitude} zoom-{zoom}.png")

    return output

    # equirectangular_to_cubemap(output)

panoids = search_panoramas(lat=latitude, lon=longitude)
panoid = panoids[0].pano_id

print(panoid)

output = get_tiles(panoid, 2)

equirectangular_to_cubemap(output, 512, latitude, longitude)

#zoom 1 - x = 2; 
#zoom 2 - x = 4; 128 repeat
#zoom 3 - x = 7;
#zoom 4 - x = 13;
#zoom 5 - x = 26

# https://jaxry.github.io/panorama-to-cubemap/
# https://matheowis.github.io/HDRI-to-CubeMap/