"""Constants for OpenKarotz integration."""

# Domain and Device Information
DOMAIN = "openkarotz"
MANUFACTURER = "Karotz"
MODEL = "OpenKarotz"

# File and Image Configuration
DEFAULT_NAME = "OpenKarotz Picture"

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
