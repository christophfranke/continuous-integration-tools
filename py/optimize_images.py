from modules import engine
from modules import out
from modules import image

@engine.prepare_and_clean
def execute():
    out.log('optimizing images...')
    image.optimize_jpg()
    image.optimize_png()

def help():
    out.log('Optimizes all images using pngopti and jpegoptim.', 'help')