import sys
import unittest
import os
import tempfile
import shutil
import contextlib
import json
import subprocess

import PIL

import templatelayer.testing_common

_APP_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_SCRIPT_PATH = os.path.join(_APP_PATH, 'templatelayer', 'resources', 'scripts')
_TOOL_FILEPATH = os.path.join(_SCRIPT_PATH, 'template_image_apply_overlays')

sys.path.insert(0, _APP_PATH)


class TestCommand(unittest.TestCase):
    def test_run(self):
        small_config = {
            "placeholders": {
                "top-left": {
                    "left": 0,
                    "top": 0,
                    "width": 50,
                    "height": 100
                },
                "top-right": {
                    "left": 50,
                    "top": 0,
                    "width": 50,
                    "height": 100
                },
                "middle-center": {
                    "left": 0,
                    "top": 100,
                    "width": 100,
                    "height": 100
                },
                "bottom-center": {
                    "left": 0,
                    "top": 200,
                    "width": 100,
                    "height": 100
                }
            }
        }

        with templatelayer.testing_common.temp_path() as temp_path:
            # Template

            template_im = \
                templatelayer.testing_common.get_new_image(
                    100,
                    300,
                    color='blue')

            template_im.save('template.png')

            # Top-Left

            component_topleft_im = \
                templatelayer.testing_common.get_new_image(
                    50,
                    100,
                    color='green')

            component_topleft_im.save('top_left.png')

            # Top-Right

            component_topright_im = \
                templatelayer.testing_common.get_new_image(
                    50,
                    100,
                    color='red')

            component_topright_im.save('top_right.png')

            # Middle-Center

            component_middlecenter_im = \
                templatelayer.testing_common.get_new_image(
                    100,
                    100,
                    color='yellow')

            component_middlecenter_im.save('middle_center.png')

            # Bottom-Center

            component_bottomcenter_im = \
                templatelayer.testing_common.get_new_image(
                    100,
                    100,
                    color='orange')

            component_bottomcenter_im.save('bottom_center.png')

            with open('config.json', 'w') as f:
                json.dump(small_config, f)

            cmd = [
                _TOOL_FILEPATH,
                'config.json',
                '--template-filepath', 'template.png',
                '--component-filepath', 'top-left', 'top_left.png',
                '--component-filepath', 'top-right', 'top_right.png',
                '--component-filepath', 'middle-center', 'middle_center.png',
                '--component-filepath', 'bottom-center', 'bottom_center.png',
                '--output-filepath', 'output.png',
            ]

            try:
                actual = \
                    subprocess.check_output(
                        cmd,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True)
            except subprocess.CalledProcessError as cpe:
                print(cpe.output)
                raise

            expected = """Applying: [top-left] [top_left.png]
Applying: [top-right] [top_right.png]
Applying: [middle-center] [middle_center.png]
Applying: [bottom-center] [bottom_center.png]
Writing.
"""

            self.assertEquals(actual, expected)
