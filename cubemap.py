from PIL import Image
from os import path, mkdir
from math import pi, atan2, hypot, floor
from numpy import clip
from threading import Thread

def get_xyz(i, j, face_id, size):

    a = 2.0 * float(i) / size
    b = 2.0 * float(j) / size

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
    inSize = imgIn.size
    outSize = imgOut.size
    inPix = imgIn.load()
    outPix = imgOut.load()
    faceSize = outSize[0]

    for xOut in range(faceSize):
        for yOut in range(faceSize):
            (x,y,z) = get_xyz(xOut, yOut, faceIdx, faceSize)
            theta = atan2(y,x)
            r = hypot(x,y)
            phi = atan2(z,r)

            uf = 0.5 * inSize[0] * (theta + pi) / pi
            vf = 0.5 * inSize[0] * (pi/2 - phi) / pi

            # Use bilinear interpolation between the four surrounding pixels
            ui = floor(uf)  # coord of pixel to bottom left
            vi = floor(vf)
            u2 = ui+1       # coords of pixel to top right
            v2 = vi+1
            mu = uf-ui      # fraction of way across pixel
            nu = vf-vi

            # Pixel values of four corners
            A = inPix[ui % inSize[0], clip(vi, 0, inSize[1]-1)]
            B = inPix[u2 % inSize[0], clip(vi, 0, inSize[1]-1)]
            C = inPix[ui % inSize[0], clip(v2, 0, inSize[1]-1)]
            D = inPix[u2 % inSize[0], clip(v2, 0, inSize[1]-1)]

            # interpolate
            (r,g,b) = (
              A[0]*(1-mu)*(1-nu) + B[0]*(mu)*(1-nu) + C[0]*(1-mu)*nu+D[0]*mu*nu,
              A[1]*(1-mu)*(1-nu) + B[1]*(mu)*(1-nu) + C[1]*(1-mu)*nu+D[1]*mu*nu,
              A[2]*(1-mu)*(1-nu) + B[2]*(mu)*(1-nu) + C[2]*(1-mu)*nu+D[2]*mu*nu )

            outPix[xOut, yOut] = (int(round(r)), int(round(g)), int(round(b)))

FACE_NAMES = {
  0: 'back',
  1: 'left',
  2: 'front',
  3: 'right',
  4: 'top',
  5: 'bottom'
}

def get_folder_path(lat, lon):
    return path.abspath(f"{lat},{lon}")

def equirectangular_to_cubemap(panorama, size, lat, lon):

    def save_face(face):
        output = Image.new("RGBA", (size, size))
        make_face(panorama, output, face)
        output.save(f"{get_folder_path(lat, lon)}\\{FACE_NAMES[face]}.png")

    try:
        mkdir(get_folder_path(lat, lon))
    except:
        print("Directory creation failed")

    for face in range(6):
        Thread(target=save_face, args=(face,)).start()