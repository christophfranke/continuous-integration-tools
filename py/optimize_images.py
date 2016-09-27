from modules import engine
from modules import out
from modules import image

@engine.prepare_and_clean
def execute(quality = None):
    out.log('optimizing images...')
    if quality is None:
        quality = 100
    image.optimize_jpg(quality)
    image.optimize_png()

def help():
    out.log('Optimizes all images using pngopti and jpegoptim.', 'help')