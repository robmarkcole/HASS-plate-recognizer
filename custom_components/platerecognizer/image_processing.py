"""Vehicle detection using Plate Recognizer cloud service."""
import logging
import requests
import voluptuous as vol

from homeassistant.components.image_processing import (
    CONF_ENTITY_ID,
    CONF_NAME,
    CONF_SOURCE,
    PLATFORM_SCHEMA,
    ImageProcessingEntity,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import split_entity_id
import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util

_LOGGER = logging.getLogger(__name__)

PLATE_READER_URL = "https://api.platerecognizer.com/v1/plate-reader/"
STATS_URL = 'https://api.platerecognizer.com/v1/statistics/'

EVENT_VEHICLE_DETECTED = "platerecognizer.vehicle_detected"

ATTR_PLATE = "plate"
ATTR_CONFIDENCE = "confidence"
ATTR_REGION_CODE = "region_code"
ATTR_VEHICLE_TYPE = "vehicle_type"

CONF_API_TOKEN = "api_token"

DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_TOKEN): cv.string,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the platform."""
    # Validate credentials by processing image.
    entities = []
    for camera in config[CONF_SOURCE]:
        platerecognizer = PlateRecognizerEntity(
            config.get(CONF_API_TOKEN),
            camera[CONF_ENTITY_ID],
            camera.get(CONF_NAME),
        )
        entities.append(platerecognizer)
    add_entities(entities)


class PlateRecognizerEntity(ImageProcessingEntity):
    """Create entity."""

    def __init__(self, api_token, camera_entity, name):
        """Init."""
        self._headers = {
            "Authorization": f"Token {api_token}",
        }
        self._camera = camera_entity
        if name:
            self._name = name
        else:
            camera_name = split_entity_id(camera_entity)[1]
            self._name = f"platerecognizer_{camera_name}"
        self._state = None
        self._results = {}
        self._vehicles = [{}]
        self._statistics = {}
        self._last_detection = None
        self.get_statistics()

    def process_image(self, image):
        """Process an image."""
        self._results = {}
        self._vehicles = [{}]
        try:
            self._results = requests.post(
                PLATE_READER_URL, files={"upload": image}, headers=self._headers
            ).json()["results"]
            self._vehicles = [
                {
                    ATTR_PLATE: r["plate"],
                    ATTR_CONFIDENCE: r["score"],
                    ATTR_REGION_CODE: r["region"]["code"],
                    ATTR_VEHICLE_TYPE: r["vehicle"]["type"],
                }
                for r in self._results
            ]
        except Exception as exc:
            _LOGGER.error("platerecognizer error processing image: %s", exc)

        self._state = len(self._vehicles)
        if self._state > 0:
            self._last_detection = dt_util.now().strftime(DATETIME_FORMAT)
            for vehicle in self._vehicles:
                self.fire_vehicle_detected_event(vehicle)
        self.get_statistics()

    def get_statistics(self):
        try:
            response = requests.get(STATS_URL, headers=self._headers).json()
            calls_remaining = response['total_calls'] - response['usage']['calls']
            response.update({'calls_remaining': calls_remaining})
            self._statistics = response.copy()
        except Exception as exc:
            _LOGGER.error("platerecognizer error getting statistics: %s", exc)

    def fire_vehicle_detected_event(self, vehicle):
        """Send event."""
        vehicle_copy = vehicle.copy()
        vehicle_copy.update({ATTR_ENTITY_ID: self.entity_id})
        self.hass.bus.fire(EVENT_VEHICLE_DETECTED, vehicle_copy)

    @property
    def camera_entity(self):
        """Return camera entity id from process pictures."""
        return self._camera

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def state(self):
        """Return the state of the entity."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return ATTR_PLATE

    @property
    def device_state_attributes(self):
        """Return the attributes."""
        attr = {}
        attr.update({"last_detection": self._last_detection})
        attr.update({"vehicles": self._vehicles})
        attr.update({"statistics": self._statistics})
        return attr
