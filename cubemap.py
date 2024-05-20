from os import path, mkdir
from math import pi, atan2, hypot, floor
from numpy import clip
from PIL import Image
from threading import Thread
from scipy import interpolate
import itertools

def get_xyz(i, j, face_id, size):

    a = 2.0 * i / size
    b = 2.0 * j / size

    if face_id == 0: # back
        (x,y,z) = (-1.0, 1.0 - a, 1.0 - b)
    elif face_id == 1: # left
        (x,y,z) = (a - 1.0, -1.0, 1.0 - b)
    elif face_id == 2: # front
        (x,y,z) = (1.0, a - 1.0, 1.0 - b)
    elif face_id == 3: # right
        (x,y,z) = (1.0 - a, 1.0, 1.0 - b)
    elif face_id == 4: # top
        (x,y,z) = (b - 1.0, a - 1.0, 1.0)
    elif face_id == 5: # bottom
        (x,y,z) = (1.0 - b, a - 1.0, -1.0)

    return (x, y, z)

def make_face(imgIn, imgOut, faceIdx):
    pano_width, pano_height = imgIn.size
    width, height = imgOut.size
    inPix = imgIn.load()

    for xOut, yOut in itertools.product(range(width), range(height)):
        x, y, z = get_xyz(xOut, yOut, faceIdx, height)
        theta = atan2(y, x)
        r = hypot(x, y)
        phi = atan2(z, r)

        uf = 0.5 * pano_width * (theta + pi) / pi
        vf = 0.5 * pano_width * (pi/2 - phi) / pi

        # TODO: optimize bilinear interpolation like crazy, generation of high res tiles should be faster

        ui = floor(uf)
        vi = floor(vf)
        u2 = ui + 1
        v2 = vi + 1
        mu = uf - ui
        nu = vf - vi

        A = inPix[ui % pano_width, clip(vi, 0, pano_height - 1)]
        B = inPix[u2 % pano_width, clip(vi, 0, pano_height - 1)]
        C = inPix[ui % pano_width, clip(v2, 0, pano_height - 1)]
        D = inPix[u2 % pano_width, clip(v2, 0, pano_height - 1)]

        color = (
            int(round(A[0]*(1-mu)*(1-nu) + B[0]*(mu)*(1-nu) + C[0]*(1-mu)*nu+D[0]*mu*nu)),
            int(round(A[1]*(1-mu)*(1-nu) + B[1]*(mu)*(1-nu) + C[1]*(1-mu)*nu+D[1]*mu*nu)),
            int(round(A[2]*(1-mu)*(1-nu) + B[2]*(mu)*(1-nu) + C[2]*(1-mu)*nu+D[2]*mu*nu))
        )

        imgOut.putpixel((xOut, yOut), color)

face_names = ["back", "left", "front", "right", "top", "bottom"]

def equirectangular_to_cubemap(panorama, size, lat, lon, zoom):

    folder_name = f"{lat},{lon} zoom-{zoom}"
    folder_path = path.abspath(folder_name)

    threads = []

    def save_face(face):
        output = Image.new("RGB", (size, size))
        make_face(panorama, output, face)
        output.save(f"{folder_path}/{folder_name} {face_names[face]}.png")

    try:
        mkdir(folder_path)
    except:
        print("Directory creation failed")

    for face in range(6):
        threads.append(Thread(target=save_face, args=(face,)))

    for t in threads:
        t.start()

    for t in threads:
        t.join()