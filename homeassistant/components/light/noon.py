"""
Support for Noon Home lights (lines).
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/light.noon/
"""
import logging

from homeassistant.components.light import (
	ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, Light)
from custom_components.noon import (
	HASSNoonEntity, NOON_ENTITIES, NOON_CONTROLLER)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['noon']


def setup_platform(hass, config, add_entities, discovery_info=None):
	
	""" Debug """
	_LOGGER.debug("Initialising Noon Lines...")
	
	"""Set up the Noon lines."""
	lines = []
	for (id, line) in hass.data[NOON_CONTROLLER].lines.items():
		_LOGGER.debug("Attempting to initialise line - {}: {}".format(id, line))
		line = HASSNoonLight(line, hass.data[NOON_CONTROLLER])
		lines.append(line)
		
	add_entities(lines, True)


class HASSNoonLight(HASSNoonEntity, Light):

	"""Representation of a Lutron Light, including dimmable."""

	def __init__(self, noon_device, controller):
		"""Initialize the light."""
		super().__init__(noon_device, controller)

	@property
	def supported_features(self):
		"""Flag supported features."""
		return SUPPORT_BRIGHTNESS

	@property
	def name(self):
		"""Return the name of the device."""
		return "{} / {}".format(self._noon_device.parentSpace.name,self._noon_device.name)

	@property
	def brightness(self):
		"""Return the brightness of the light."""
		return round(self._noon_device.dimmingLevel * (255/100))

	def turn_on(self, **kwargs):

		"""Turn the light on."""
		if ATTR_BRIGHTNESS in kwargs:
			brightness = round(kwargs[ATTR_BRIGHTNESS] * (100/255))
		elif self._noon_device.dimmingLevel == 0:
			brightness = 100
		else:
			brightness = self._noon_device.dimmingLevel
		self._noon_device.set_brightness(brightness)

	def turn_off(self, **kwargs):

		"""Turn the light off."""
		self._noon_device.turn_off()

	@property
	def device_state_attributes(self):
		"""Return the state attributes."""
		attr = {}
		return attr

	@property
	def is_on(self):
		"""Return true if device is on."""
		return (self._noon_device.lineState == "on")

	def update(self):
		"""Call when forcing a refresh of the device."""
		pass