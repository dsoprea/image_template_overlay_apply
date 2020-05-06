import os
import tempfile
import shutil
import contextlib

import PIL.Image

def get_new_image(width, height, color=(0, 0, 0)):
    mode = 'RGB'
    size = (width, height)

    template_im = PIL.Image.new(mode, size, color=color)
    return template_im

@contextlib.contextmanager
def temp_path():
    original_wd = os.getcwd()

    temp_path = tempfile.mkdtemp()
    os.chdir(temp_path)

    try:
        yield temp_path
    finally:
        os.chdir(original_wd)

        try:
            shutil.rmtree(temp_path)
        except:
            pass
