"""Constants for OpenKarotz integration."""

# Domain and Device Information
DOMAIN = "openkarotz"
MANUFACTURER = "Karotz"
MODEL = "OpenKarotz"

# File and Image Configuration
FILENAME = "SelectedKarotzPicture.jpg"
DEFAULT_NAME = "OpenKarotz Picture"

# Snapshot Configuration
SNAPSHOT_SELECT_ENTITY = "select.openkarotz_snapshots"
SNAPSHOT_URL_TEMPLATE = "http://{host}/cgi-bin/snapshot_get?filename={filename}"

# Device IDs for Entity Organization
DEVICE_KAROTZ = "karotz"
DEVICE_EARS = "karotz_ears"
DEVICE_LEDS = "karotz_leds"
DEVICE_SOUND = "karotz_sound"
DEVICE_PICTURE = "karotz_picture"

# Entity IDs for State Access
ENTITY_VOICE_SELECT = "select.openkarotz_voice"
ENTITY_MOOD_SELECT = "select.openkarotz_mood"
ENTITY_RADIOS_SELECT = "select.openkarotz_radios"
ENTITY_SOUND_SELECT = "select.openkarotz_sound"
ENTITY_SNAPSHOTS_SELECT = "select.openkarotz_snapshots"

ENTITY_EAR_LEFT = "number.openkarotz_ear_left"
ENTITY_EAR_RIGHT = "number.openkarotz_ear_right"
ENTITY_PULSE_SPEED = "number.openkarotz_pulse_speed"

ENTITY_TTS_TEXT = "text.openkarotz_tts"

ENTITY_LED_COLOR_1 = "light.openkarotz_color_1"
ENTITY_LED_COLOR_2 = "light.openkarotz_color_2"
ENTITY_LED_PULSE = "switch.openkarotz_led_pulse"

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
