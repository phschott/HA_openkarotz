"""Constants for OpenKarotz integration."""

# Domain and Device Information
DOMAIN = "openkarotz"
MANUFACTURER = "Karotz"
MODEL = "OpenKarotz"

# Config entry keys and defaults
CONF_NAME = "name"
# Default Karotz name. Its slug ("openkarotz") is the entity_id prefix, so a
# Karotz keeping this name gets the historical entity_ids used by
# dashboard.yaml (e.g. switch.openkarotz_led_pulse).
DEFAULT_KAROTZ_NAME = "OpenKarotz"

# Max number of snapshot images kept in memory. Bytes are fetched from the
# device on demand through Home Assistant's authenticated image proxy and
# cached here (never written under config/www, which would expose the
# rabbit's photos unauthenticated at /local/...).
SNAPSHOT_IMAGE_CACHE_SIZE = 12

# Number of "slot" image entities exposed for the native clickable gallery.
# Slot 1 is the most recent snapshot, slot 2 the second most recent, etc.
SNAPSHOT_SLOT_COUNT = 12

# Seconds to wait after taking a photo before re-reading the snapshot list,
# giving the device time to store the new file so the gallery picks it up.
SNAPSHOT_REFRESH_DELAY = 3

# Device IDs for Entity Organization
DEVICE_KAROTZ = "karotz"
DEVICE_EARS = "karotz_ears"
DEVICE_LEDS = "karotz_leds"
DEVICE_SOUND = "karotz_sound"
DEVICE_PICTURE = "karotz_picture"

# Device name = "<Karotz name> <suffix>", e.g. "Kitchen Ears".
DEVICE_NAME_SUFFIXES = {
    DEVICE_KAROTZ: "",
    DEVICE_EARS: "Ears",
    DEVICE_LEDS: "LEDs",
    DEVICE_SOUND: "Sound",
    DEVICE_PICTURE: "Picture",
}

# Coordinator Update Intervals (in seconds)
COORDINATOR_UPDATE_INTERVAL = 14400  # 4 hours
COORDINATOR_FAST_UPDATE_INTERVAL = 5  # 5 seconds

# Ear Configuration
EAR_MIN_VALUE = 0
EAR_MAX_VALUE = 16
EAR_DEFAULT_VALUE = 8

# LED Pulse Speed Configuration
LED_SPEED_MIN_VALUE = 0
LED_SPEED_MAX_VALUE = 2000
LED_SPEED_DEFAULT_VALUE = 700

# Platform list
PLATFORMS = ["sensor", "button", "select", "text", "number", "light", "switch", "image"]
