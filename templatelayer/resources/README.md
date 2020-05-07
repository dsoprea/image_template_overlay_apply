[![Build Status](https://travis-ci.org/dsoprea/image_template_overlay_apply.svg?branch=master)](https://travis-ci.org/dsoprea/image_template_overlay_apply) [![Coverage Status](https://coveralls.io/repos/github/dsoprea/image_template_overlay_apply/badge.svg?branch=master)](https://coveralls.io/github/dsoprea/image_template_overlay_apply?branch=master)

# Overview

This is a library and tool that streamlines applying component images to a template image. A config is provided that defines boundaries of the regions within the template image to apply the component images to.

There is strictness to prevent overlapping configs and additional support for determining coverage of the template image.

Masking is not current supported.


# Installation

```
$ sudo pip install image_template_overlay_apply
```

You may choose to clone the project instead:

```
$ git clone https://github.com/dsoprea/image_template_overlay_apply.git
$ cd image_template_overlay_apply
$ sudo pip install -e .
```


# Library Usage

It is recommended that you use the source-code of the [tool](https://github.com/dsoprea/image_template_overlay_apply/blob/master/templatelayer/resources/scripts/template_image_apply_overlays) as a roadmap to using the library. There is also excellent [unit-test coverage](https://github.com/dsoprea/image_template_overlay_apply/blob/master/tests) that may be used for guidance.


# Tool Usage

The tool has [full command-line documentation](https://github.com/dsoprea/image_template_overlay_apply/blob/master/templatelayer/resources/scripts/template_image_apply_overlays). You can also read the template from STDIN and write the output image to STDOUT (using the same format as the input).


## Example

Using example data in *assets/example*.

Config:

```json
{
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
```

Running:

```
$ template_image_apply_overlays \
    assets/example/layout.json \
    --template-filepath assets/example/template.png \
    --component-filepath top-left assets/example/top_left.png \
    --component-filepath top-right assets/example/top_right.png \
    --component-filepath middle-center assets/example/middle_center.png \
    --component-filepath bottom-center assets/example/bottom_center.png \
    --output-filepath /tmp/output.png

Applying: [top-left] [top_left.png]
Applying: [top-right] [top_right.png]
Applying: [middle-center] [middle_center.png]
Applying: [bottom-center] [bottom_center.png]
Writing.
```

The output will look like:

![example output](https://github.com/dsoprea/image_template_overlay_apply/blob/master/assets/example/output.png "Example Output")


# Tests

To run the unit-tests:

```
$ nose2 -v tests
```
