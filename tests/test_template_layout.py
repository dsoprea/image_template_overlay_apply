import unittest
import json

import PIL.Image

import templatelayer.template_layout
import templatelayer.testing_common

_TEST_GOOD_LAYOUT_CONFIG = u"""\
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
"""


class TestSimpleTemplateLayout(unittest.TestCase):
    def _get_empty_template_image(self):
        template_im = \
            templatelayer.testing_common.get_new_image(
                100,
                300)

        return template_im

    def _get_basic_object(self, template_im=None, config=None):
        if template_im is None:
            template_im = self._get_empty_template_image()

        if config is None:
            config = _TEST_GOOD_LAYOUT_CONFIG

        lc = json.loads(config)
        tl = templatelayer.template_layout.SimpleTemplateLayout(template_im, lc)

        return tl

    def _get_pixels(self, im):
        current_pixels = im.getdata()
        for pixel in current_pixels:
            yield pixel

    def test_parse_and_validate(self):
        # This will already parse the config once, but may not catch subtle errors.
        tl = self._get_basic_object()

        lc = json.loads(_TEST_GOOD_LAYOUT_CONFIG)
        actual = tl._parse_and_validate(lc)

        expected = {
            'bottom-center': templatelayer.template_layout._PLACEHOLDER(name='bottom-center', top=200, left=0, height=100, width=100),
            'top-right': templatelayer.template_layout._PLACEHOLDER(name='top-right', top=0, left=50, height=100, width=50),
            'top-left': templatelayer.template_layout._PLACEHOLDER(name='top-left', top=0, left=0, height=100, width=50),
            'middle-center': templatelayer.template_layout._PLACEHOLDER(name='middle-center', top=100, left=0, height=100, width=100),
        }

        self.assertEquals(actual, expected)

    def test_parse_and_validate_placeholder(self):
        # This will already parse the config once, but may not catch subtle errors.
        tl = self._get_basic_object()

        parameters = {
            "left": 0,
            "top": 0,
            "width": 50,
            "height": 100
        }

        placeholder_configs = {}

        actual = \
            tl._parse_and_validate_placeholder(
                'test-placeholder',
                parameters,
                placeholder_configs)

        expected = \
            templatelayer.template_layout._PLACEHOLDER(
                name='test-placeholder',
                top=0,
                left=0,
                height=100,
                width=50)

        self.assertEquals(actual, expected)

    def test_assert_no_overlap__ok(self):
        tl = self._get_basic_object()

        ph = templatelayer.template_layout._PLACEHOLDER(name='top-left', top=0, left=0, height=100, width=50)
        other_ph = templatelayer.template_layout._PLACEHOLDER(name='top-right', top=0, left=50, height=100, width=50)

        tl._assert_no_overlap(ph, other_ph)

    def test_assert_no_overlap__leftright_overlap_1(self):
        tl = self._get_basic_object()

        ph = templatelayer.template_layout._PLACEHOLDER(name='top-left', top=0, left=0, height=100, width=50)
        other_ph = templatelayer.template_layout._PLACEHOLDER(name='top-right', top=0, left=49, height=100, width=50)

        try:
            tl._assert_no_overlap(ph, other_ph)
        except templatelayer.template_layout.PlaceholderOverlapError as e:
            expected = "Placeholder [top-left] overlaps with placeholder [top-right]."
            if str(e) != expected:
                raise
        else:
            raise Exception("Expected overlap.")

    def test_assert_no_overlap__leftright_overlap_2(self):
        tl = self._get_basic_object()

        ph = templatelayer.template_layout._PLACEHOLDER(name='top-left', top=0, left=0, height=100, width=51)
        other_ph = templatelayer.template_layout._PLACEHOLDER(name='top-right', top=0, left=50, height=100, width=50)

        try:
            tl._assert_no_overlap(ph, other_ph)
        except templatelayer.template_layout.PlaceholderOverlapError as e:
            expected = "Placeholder [top-left] overlaps with placeholder [top-right]."
            if str(e) != expected:
                raise
        else:
            raise Exception("Expected overlap.")

    def test_assert_no_overlap__topbottom_overlap_1(self):
        tl = self._get_basic_object()

        ph = templatelayer.template_layout._PLACEHOLDER(name='middle-center', top=100, left=0, height=100, width=100)
        other_ph = templatelayer.template_layout._PLACEHOLDER(name='bottom-center', top=199, left=0, height=100, width=100)

        try:
            tl._assert_no_overlap(ph, other_ph)
        except templatelayer.template_layout.PlaceholderOverlapError as e:
            expected = "Placeholder [middle-center] overlaps with placeholder [bottom-center]."
            if str(e) != expected:
                raise
        else:
            raise Exception("Expected overlap.")

    def test_assert_no_overlap__topbottom_overlap_2(self):
        tl = self._get_basic_object()

        ph = templatelayer.template_layout._PLACEHOLDER(name='middle-center', top=100, left=0, height=101, width=100)
        other_ph = templatelayer.template_layout._PLACEHOLDER(name='bottom-center', top=200, left=0, height=100, width=100)

        try:
            tl._assert_no_overlap(ph, other_ph)
        except templatelayer.template_layout.PlaceholderOverlapError as e:
            expected = "Placeholder [middle-center] overlaps with placeholder [bottom-center]."
            if str(e) != expected:
                raise
        else:
            raise Exception("Expected overlap.")

    def test_assert_no_overlap__full_overlap(self):
        tl = self._get_basic_object()

        ph = templatelayer.template_layout._PLACEHOLDER(name='small', top=20, left=20, height=20, width=20)
        other_ph = templatelayer.template_layout._PLACEHOLDER(name='big', top=0, left=0, height=100, width=100)

        try:
            tl._assert_no_overlap(ph, other_ph)
        except templatelayer.template_layout.PlaceholderOverlapError as e:
            expected = "Placeholder [small] overlaps with placeholder [big]."
            if str(e) != expected:
                raise
        else:
            raise Exception("Expected overlap.")

    def test_supported_placeholder_names(self):
        tl = self._get_basic_object()

        expected_supported_placeholder_names = sorted([
            'bottom-center',
            'top-right',
            'top-left',
            'middle-center',
        ])

        self.assertEquals(
            sorted(tl.supported_placeholder_names),
            expected_supported_placeholder_names)

        self.assertEquals(tl.applied_placeholder_names, [])
        self.assertEquals(sorted(tl.unapplied_placeholder_names), expected_supported_placeholder_names)
        self.assertFalse(tl.is_completely_applied)

    def test_get_placeholder_config__known(self):
        tl = self._get_basic_object()

        actual = {}
        for name in sorted(tl.supported_placeholder_names):
            ph = tl.get_placeholder_config(name)
            actual[ph.name] = ph

        expected = {
            'bottom-center': templatelayer.template_layout._PLACEHOLDER(name='bottom-center', top=200, left=0, height=100, width=100),
            'top-right': templatelayer.template_layout._PLACEHOLDER(name='top-right', top=0, left=50, height=100, width=50),
            'top-left': templatelayer.template_layout._PLACEHOLDER(name='top-left', top=0, left=0, height=100, width=50),
            'middle-center': templatelayer.template_layout._PLACEHOLDER(name='middle-center', top=100, left=0, height=100, width=100),
        }

        self.assertEquals(actual, expected)

    def test_get_placeholder_config__unknown(self):
        tl = self._get_basic_object()

        try:
            tl.get_placeholder_config('unknown-placeholder')
        except templatelayer.template_layout.UnknownPlaceholderException:
            pass
        else:
            raise Exception("Expected exception for unknown placeholder.")

    def test_validate_image_for_placeholder(self):
        tl = self._get_basic_object()
        for name in tl.supported_placeholder_names:
            ph = tl.get_placeholder_config(name)

            placeholder_im = \
                templatelayer.testing_common.get_new_image(
                    ph.width,
                    ph.height)

            tl.validate_image_for_placeholder(name, placeholder_im)

    def test_apply_component__one(self):
        tl = self._get_basic_object()

        ph = tl.get_placeholder_config('bottom-center')

        placeholder_im = \
            templatelayer.testing_common.get_new_image(
                ph.width,
                ph.height)

        tl.apply_component(ph.name, placeholder_im)


        self.assertFalse(tl.is_completely_applied)

        expected_supported_placeholder_names = sorted([
            'bottom-center',
            'middle-center',
            'top-left',
            'top-right',
        ])

        self.assertEquals(
            sorted(tl.supported_placeholder_names),
            expected_supported_placeholder_names)

        expected_applied_placeholder_names = sorted([
            'bottom-center',
        ])

        self.assertEquals(
            sorted(tl.applied_placeholder_names),
            expected_applied_placeholder_names)

        expected_unapplied_placeholder_names = sorted([
            'middle-center',
            'top-left',
            'top-right',
        ])

        self.assertEquals(
            sorted(tl.unapplied_placeholder_names),
            expected_unapplied_placeholder_names)

    def test_apply_component__multiple_some(self):
        tl = self._get_basic_object()

        ph = tl.get_placeholder_config('bottom-center')
        placeholder_im = \
            templatelayer.testing_common.get_new_image(
                ph.width,
                ph.height)

        tl.apply_component(ph.name, placeholder_im)

        ph = tl.get_placeholder_config('middle-center')
        placeholder_im = \
            templatelayer.testing_common.get_new_image(
                ph.width,
                ph.height)

        tl.apply_component(ph.name, placeholder_im)

        self.assertFalse(tl.is_completely_applied)

        expected_supported_placeholder_names = sorted([
            'bottom-center',
            'middle-center',
            'top-left',
            'top-right',
        ])

        self.assertEquals(
            sorted(tl.supported_placeholder_names),
            expected_supported_placeholder_names)

        expected_applied_placeholder_names = sorted([
            'bottom-center',
            'middle-center',
        ])

        self.assertEquals(
            sorted(tl.applied_placeholder_names),
            expected_applied_placeholder_names)

        expected_unapplied_placeholder_names = sorted([
            'top-left',
            'top-right',
        ])

        self.assertEquals(
            sorted(tl.unapplied_placeholder_names),
            expected_unapplied_placeholder_names)

    def test_apply_component__multiple_all(self):
        tl = self._get_basic_object()
        for name in tl.supported_placeholder_names:
            ph = tl.get_placeholder_config(name)
            placeholder_im = \
                templatelayer.testing_common.get_new_image(
                    ph.width,
                    ph.height)

            tl.apply_component(name, placeholder_im)

        self.assertTrue(tl.is_completely_applied)

        expected_supported_placeholder_names = sorted([
            'bottom-center',
            'middle-center',
            'top-left',
            'top-right',
        ])

        self.assertEquals(
            sorted(tl.supported_placeholder_names),
            expected_supported_placeholder_names)

        self.assertEquals(
            sorted(tl.applied_placeholder_names),
            expected_supported_placeholder_names)

        self.assertEquals(
            tl.unapplied_placeholder_names,
            [])

    def test_apply_component__multiple_all__check_image(self):
        small_config = u"""\
{
    "placeholders": {
        "top-left": {
            "left": 0,
            "top": 0,
            "width": 2,
            "height": 2
        },
        "top-right": {
            "left": 2,
            "top": 0,
            "width": 2,
            "height": 2
        },
        "middle-center": {
            "left": 0,
            "top": 2,
            "width": 4,
            "height": 2
        },
        "bottom-center": {
            "left": 0,
            "top": 4,
            "width": 4,
            "height": 2
        }
    }
}
"""

        template_im = \
            templatelayer.testing_common.get_new_image(
                4,
                6)

        tl = self._get_basic_object(
                template_im=template_im,
                config=small_config)

        actual_initial_pixels = self._get_pixels(tl.resource)
        actual_initial_pixels = list(actual_initial_pixels)

        expected_initial_pixels = [
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
        ]

        self.assertEquals(actual_initial_pixels, expected_initial_pixels)

        # Overlay top-left.

        placeholder_im = \
            templatelayer.testing_common.get_new_image(
                2,
                2,
                color=(1, 1, 1))

        tl.apply_component('top-left', placeholder_im)

        actual_current_pixels = self._get_pixels(tl.resource)
        actual_current_pixels = list(actual_current_pixels)

        expected_current_pixels = [
            (1, 1, 1), (1, 1, 1), (0, 0, 0), (0, 0, 0),
            (1, 1, 1), (1, 1, 1), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
        ]

        self.assertEquals(actual_current_pixels, expected_current_pixels)

        # Overlay top-right.

        placeholder_im = \
            templatelayer.testing_common.get_new_image(
                2,
                2,
                color=(2, 2, 2))

        tl.apply_component('top-right', placeholder_im)

        actual_current_pixels = self._get_pixels(tl.resource)
        actual_current_pixels = list(actual_current_pixels)

        expected_current_pixels = [
            (1, 1, 1), (1, 1, 1), (2, 2, 2), (2, 2, 2),
            (1, 1, 1), (1, 1, 1), (2, 2, 2), (2, 2, 2),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
        ]

        self.assertEquals(actual_current_pixels, expected_current_pixels)

        # Overlay middle-center.

        placeholder_im = \
            templatelayer.testing_common.get_new_image(
                4,
                2,
                color=(3, 3, 3))

        tl.apply_component('middle-center', placeholder_im)

        actual_current_pixels = self._get_pixels(tl.resource)
        actual_current_pixels = list(actual_current_pixels)

        expected_current_pixels = [
            (1, 1, 1), (1, 1, 1), (2, 2, 2), (2, 2, 2),
            (1, 1, 1), (1, 1, 1), (2, 2, 2), (2, 2, 2),
            (3, 3, 3), (3, 3, 3), (3, 3, 3), (3, 3, 3),
            (3, 3, 3), (3, 3, 3), (3, 3, 3), (3, 3, 3),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
            (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
        ]

        self.assertEquals(actual_current_pixels, expected_current_pixels)

        # Overlay bottom-center.

        placeholder_im = \
            templatelayer.testing_common.get_new_image(
                4,
                2,
                color=(4, 4, 4))

        tl.apply_component('bottom-center', placeholder_im)

        actual_current_pixels = self._get_pixels(tl.resource)
        actual_current_pixels = list(actual_current_pixels)

        expected_current_pixels = [
            (1, 1, 1), (1, 1, 1), (2, 2, 2), (2, 2, 2),
            (1, 1, 1), (1, 1, 1), (2, 2, 2), (2, 2, 2),
            (3, 3, 3), (3, 3, 3), (3, 3, 3), (3, 3, 3),
            (3, 3, 3), (3, 3, 3), (3, 3, 3), (3, 3, 3),
            (4, 4, 4), (4, 4, 4), (4, 4, 4), (4, 4, 4),
            (4, 4, 4), (4, 4, 4), (4, 4, 4), (4, 4, 4),
        ]

        self.assertEquals(actual_current_pixels, expected_current_pixels)

    def test_apply_component__unknown_placeholder(self):
        tl = self._get_basic_object()

        try:
            tl.apply_component("unknown-placehodler", None)
        except templatelayer.template_layout.UnknownPlaceholderException:
            pass
        else:
            raise Exception("Expected exception for unknown placeholder.")

    def test_placeholder_total_coverage(self):
        # With one placeholder.

        small_config = u"""\
{
    "placeholders": {
        "top-left": {
            "left": 0,
            "top": 0,
            "width": 2,
            "height": 2
        }
    }
}
"""

        template_im = \
            templatelayer.testing_common.get_new_image(
                4,
                6)

        tl = self._get_basic_object(
                template_im=template_im,
                config=small_config)

        self.assertEquals(tl.placeholder_total_coverage, (4, 24))
        self.assertFalse(tl.is_covered)


        # With two placeholders.

        small_config = u"""\
{
    "placeholders": {
        "top-left": {
            "left": 0,
            "top": 0,
            "width": 2,
            "height": 2
        },
        "top-right": {
            "left": 2,
            "top": 0,
            "width": 2,
            "height": 2
        }
    }
}
"""

        template_im = \
            templatelayer.testing_common.get_new_image(
                4,
                6)

        tl = self._get_basic_object(
                template_im=template_im,
                config=small_config)

        self.assertEquals(tl.placeholder_total_coverage, (8, 24))
        self.assertFalse(tl.is_covered)


        # With three placeholders.

        small_config = u"""\
{
    "placeholders": {
        "top-left": {
            "left": 0,
            "top": 0,
            "width": 2,
            "height": 2
        },
        "top-right": {
            "left": 2,
            "top": 0,
            "width": 2,
            "height": 2
        },
        "middle-center": {
            "left": 0,
            "top": 2,
            "width": 4,
            "height": 2
        }
    }
}
"""

        template_im = \
            templatelayer.testing_common.get_new_image(
                4,
                6)

        tl = self._get_basic_object(
                template_im=template_im,
                config=small_config)

        self.assertEquals(tl.placeholder_total_coverage, (16, 24))
        self.assertFalse(tl.is_covered)


        # With four placeholders.

        small_config = u"""\
{
    "placeholders": {
        "top-left": {
            "left": 0,
            "top": 0,
            "width": 2,
            "height": 2
        },
        "top-right": {
            "left": 2,
            "top": 0,
            "width": 2,
            "height": 2
        },
        "middle-center": {
            "left": 0,
            "top": 2,
            "width": 4,
            "height": 2
        },
        "bottom-center": {
            "left": 0,
            "top": 4,
            "width": 4,
            "height": 2
        }
    }
}
"""

        template_im = \
            templatelayer.testing_common.get_new_image(
                4,
                6)

        tl = self._get_basic_object(
                template_im=template_im,
                config=small_config)

        self.assertEquals(tl.placeholder_total_coverage, (24, 24))
        self.assertTrue(tl.is_covered)
