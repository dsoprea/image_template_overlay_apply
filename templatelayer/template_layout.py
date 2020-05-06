import logging
import json
import collections

_LOGGER = logging.getLogger(__name__)

_PLACEHOLDER = \
    collections.namedtuple(
        '_PLACEHOLDER', [
            'name',
            'top',
            'left',
            'height',
            'width',
        ])


class TemplateLayoutException(Exception):
    pass


class PlaceholderNotCompatibleException(TemplateLayoutException):
    pass


class PlaceholderOverlapError(TemplateLayoutException):
    pass


class UnknownPlaceholderException(TemplateLayoutException):
    pass


class SimpleTemplateLayout(object):
    def __init__(self, template_im, config):
        """Initialize with the template IM object and the file-like resource
        with the layout config.
        """

        placeholder_configs = self._parse_and_validate(config)
        self._placeholder_configs = placeholder_configs

        self._applied_placeholders_s = set()

        self._base_im = template_im

    def _parse_and_validate(self, layout):
        """Process the whole config."""

        placeholders = layout.get('placeholders')

        assert \
            issubclass(placeholders.__class__, dict) is True, \
            "Layout config must have 'placeholders' dictionary/object."

        assert \
            placeholders, \
            "At least one placeholder must be configured."

        placeholder_configs = {}
        for name, parameters in placeholders.items():
            ph = self._parse_and_validate_placeholder(
                    name,
                    parameters,
                    placeholder_configs)

            placeholder_configs[name] = ph

        return placeholder_configs

    def _parse_and_validate_placeholder(
            self, name, parameters, placeholder_configs):
        """Validates and loads a single placeholder definition from the config.
        """

        try:
            ph = \
                _PLACEHOLDER(
                    name=name,
                    top=parameters['top'],
                    left=parameters['left'],
                    height=parameters['height'],
                    width=parameters['width'])
        except KeyError:
            _LOGGER.exception("One or more placeholder parameters are missing "
                              "for [{}].".format(name))

            raise

        # Check for overlaps.

        for other_ph in placeholder_configs.values():
            self._assert_no_overlap(ph, other_ph)

        return ph

    def _assert_no_overlap(self, ph, other_ph):
        """Make sure the given placeholder-config doesn't overlap with any
        previous placeholder-configurations.
        """

        # Check horizontal position.

        is_in_left_right_boundaries = False

        other_right = other_ph.left + other_ph.width

        left_is_in_range = ph.left >= other_ph.left and ph.left < other_right
        if left_is_in_range is True:
            is_in_left_right_boundaries = True

        right = ph.left + ph.width
        right_is_in_range = right > other_ph.left and right < other_right
        if right_is_in_range is True:
            is_in_left_right_boundaries = True

        # Check vertical_position.

        is_in_top_bottom_boundaries = False

        other_bottom = other_ph.top + other_ph.height

        top_is_in_range = ph.top >= other_ph.top and ph.top < other_bottom
        if top_is_in_range is True:
            is_in_top_bottom_boundaries = True

        bottom = ph.top + ph.height
        if bottom > other_ph.top and bottom < other_bottom:
            is_in_top_bottom_boundaries = True

        if is_in_left_right_boundaries is True and \
           is_in_top_bottom_boundaries is True:
            raise PlaceholderOverlapError(
                    "Placeholder [{}] overlaps with placeholder [{}].".format(
                    ph.name, other_ph.name))

    def get_placeholder_config(self, name):
        """Retrieved a single placeholder config."""

        try:
            return self._placeholder_configs[name]
        except KeyError:
            pass

        raise UnknownPlaceholderException(name)

    def validate_image_for_placeholder(self, name, im):
        """Check whether the given image is compatible with the given
        placeholder.
        """

        config = self.get_placeholder_config(name)

        if config.width != im.width or config.height != im.height:
            raise PlaceholderNotCompatibleException(
                "Image with size ({}, {}) not compatible with placeholder "
                "[{}] size ({}, {}).".format(
                im.width, im.height, config.width, config.height))

        return config

    def apply_component(self, name, overlay_im):
        """Overlay the given image to the specific configured area of the
        placeholder.
        """

# TODO(dustin): Add support for masking (for irregular shapes) later, if/when it comes up.

        assert \
            name not in self._applied_placeholders_s, \
            "Placeholder name not unique: [{}]".format(name)

        config = self.validate_image_for_placeholder(name, overlay_im)

        offset = (config.left, config.top)
        self._base_im.paste(overlay_im, offset)

        self._applied_placeholders_s.add(name)

    def apply_components(self, im_mapping):
        """Apply multiple overlays."""

        for name, overlay_im in im_mapping.items():
            self.apply_component(name, overlay_im)

    @property
    def supported_placeholder_names(self):
        """Return the names of all config-supported placeholder."""

        return list(self._placeholder_configs.keys())

    @property
    def applied_placeholder_names(self):
        """Return the names of placeholders that have had overlays applied to
        them.
        """

        return list(self._applied_placeholders_s)

    @property
    def unapplied_placeholder_names(self):
        """Return the names of placeholders that have not yet had overlays
        applied to them.
        """

        all_placeholders_s = set(self._placeholder_configs.keys())
        return list(all_placeholders_s - self._applied_placeholders_s)

    @property
    def is_completely_applied(self):
        """Returns whether all placeholders have been overlayed."""

        has_unapplied_placeholders = bool(self.unapplied_placeholder_names)
        return has_unapplied_placeholders is False

    @property
    def resource(self):
        return self._base_im

    @property
    def placeholder_total_coverage(self):
        """Returns a 2-tuple describing a rational of how much of the template
        image is covered by placeholders (in terms of box overlays).
        """

        configs = self._placeholder_configs.copy()
        _, first_ph = configs.popitem()

        left = first_ph.left
        right = first_ph.left + first_ph.width
        top = first_ph.top
        bottom = first_ph.top + first_ph.height
        for ph in configs.values():
            left = min(left, ph.left)
            right = max(right, ph.left + ph.width)
            top = min(top, ph.top)
            bottom = max(bottom, ph.top + ph.height)

        placeholder_size = (right - left) * (bottom - top)
        template_size = self._base_im.width * self._base_im.height

        return (placeholder_size, template_size)

    @property
    def is_covered(self):
        """Returns whether every pixel of the template is covered by
        placeholders.
        """

        placeholder_coverage, template_size = self.placeholder_total_coverage
        return placeholder_coverage == template_size
