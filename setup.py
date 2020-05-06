import os
import sys
import setuptools

import templatelayer

_DESCRIPTION = """\
Takes an image that has placeholders and applies separate component issues to
it.
"""

_APP_PATH = os.path.dirname(templatelayer.__file__)

with open(os.path.join(_APP_PATH, 'resources', 'README.md'), 'rt') as f:
    long_description = f.read()

with open(os.path.join(_APP_PATH, 'resources', 'requirements.txt'), 'rt') as f:
    install_requires = [s.strip() for s in f.readlines()]

setuptools.setup(
    name='templatelayer',
    version=templatelayer.__version__,
    description=_DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Dustin Oprea',
    author_email='myselfasunder@gmail.com',
    url='https://github.com/dsoprea/image_template_layer_apply',
    license='MIT',
    packages=setuptools.find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    scripts=[
        # 'templatelayer/resources/scripts/finish_template_image',
    ],
    install_requires=install_requires,
)
