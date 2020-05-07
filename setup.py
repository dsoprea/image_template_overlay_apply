import os
import sys
import setuptools

import templatelayer

# This can't be more than one line or it'll be misinterpreted as the long-
# description.
_DESCRIPTION = """\
Takes an image that has placeholders and applies separate component issues to it."""

_APP_PATH = os.path.dirname(templatelayer.__file__)

with open(os.path.join(_APP_PATH, 'resources', 'README.md'), 'rt') as f:
    long_description = f.read()

with open(os.path.join(_APP_PATH, 'resources', 'requirements.txt'), 'rt') as f:
    install_requires = [s.strip() for s in f.readlines()]

setuptools.setup(
    name='image_template_overlay_apply',
    version=templatelayer.__version__,
    description=_DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Dustin Oprea',
    author_email='myselfasunder@gmail.com',
    url='https://github.com/dsoprea/image_template_overlay_apply',
    license='MIT',
    packages=setuptools.find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    scripts=[
        'templatelayer/resources/scripts/template_image_apply_overlays',
    ],
    install_requires=install_requires,
)
