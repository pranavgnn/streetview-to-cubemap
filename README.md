### Google StreetView to CubeMap converter

Given a latitude and a longitude and a zoom level, the program picks up all the tiles from google maps that make up the equirectangular image, stitch them up, and then convert them to the 6 cube faces. Pipes 6 images into a directory `{lat},{lon} zoom-{zoomLevel}`