### Google StreetView to CubeMap converter

Given a latitude and a longitude and a zoom level, the program picks up all the tiles from google maps that make up the equirectangular image, stitch them up to make up a single equirectangular image, and then convert it to 6 planar images that are oriented to 6 sides of a cube. Pipes 6 images into a directory `{lat},{lon} zoom-{zoomLevel}`