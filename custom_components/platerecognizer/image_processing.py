"""Person detection using Sighthound cloud service."""
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

PLATE_READER_URL = 'https://api.platerecognizer.com/v1/plate-reader/'

EVENT_VEHICLE_DETECTED = "platerecognizer.vehicle_detected"

ATTR_PLATE = "plate"
ATTR_CONFIDENCE = "confidence"
CONF_API_TOKEN = "api_token"


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
            api_token,
            camera[CONF_ENTITY_ID],
            camera.get(CONF_NAME),
        )
        entities.append(platerecognizer)
    add_entities(entities)


class PlateRecognizerEntity(ImageProcessingEntity):
    """Create entity."""

    def __init__(
        self, api_token, camera_entity, name
    ):
        """Init."""
        self._headers = {
            'Authorization': f'Token {api_token}',
        }
        self._camera = camera_entity
        if name:
            self._name = name
        else:
            camera_name = split_entity_id(camera_entity)[1]
            self._name = f"platerecognizer_{camera_name}"
        self._state = None
        self._plates = []
        self._last_detection = None

    def process_image(self, image):
        """Process an image."""
        self._plates = []
        try:
            response = requests.post(PLATE_READER_URL, files={"upload": image}, headers=headers).json()
        except Exception as exc:
            _LOGGER.error("platerecognizer error : %s", exc)
        self._plates = [{'plate': r['plate'], 'score':r['score']} for r in response['results']] 

        self._state = len(self._plates)
        if self._state > 0:
            self._last_detection = dt_util.now().strftime(DATETIME_FORMAT)

    def fire_vehicle_detected_event(self, vehicle):
        """Send event."""
        self.hass.bus.fire(
            EVENT_VEHICLE_DETECTED,
            {
                ATTR_ENTITY_ID: self.entity_id,
                ATTR_PLATE: vehicle["licenseplate"],
                ATTR_VEHICLE_TYPE: vehicle["vehicleType"],
                ),
            },
        )

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
        attr.update({"last_plate": self._last_detection})
        attr.update({"plates": self._plates})
        return attr
