# OpenKarotz HomeAssistant integration
This is a standard integration of OpenKarotz ([Free Rabbits](https://www.freerabbits.nl) version) into Home Assistant.

Please make sure you have installed OpenKarotz on Free Rabbits OS, as we are using APIs from OpenKarotz to interact with your rabbit.

## Currently Supported features
- Sensors to retrieve rabbit status (Using */cgi-bin/status* api): Version, used space, # of tags, # of Stories, # of sounds, # of Moods, Mac address
- Put rabbit to sleep (Using */cgi-bin/sleep* api)
- Wake up rabbit (Using */cgi-bin/wakeup* api)
- Reboot rabbit (Using */cgi-bin/reboot* api)
- Get Number of snapshots (Using *//cgi-bin/snapshot_list* api)
- Take snapshot (Using */cgi-bin/snapshot* api)
- Clear snapshots (Using */cgi-bin/clear_snapshots* api)
- Move ears (Using *"/cgi-bin/ears* api)
- Move ears random (Using */cgi-bin/ears_random* api)
- Reset ears (Using */cgi-bin/ears_reset* api)
- Play Mood (Using */cgi-bin/apps/moods* api)
- Play Clock (Using */cgi-bin/apps/clock* api)
- Speach (Using */cgi-bin/tts?voice={voice}&text={text}* api)
- Change color (Using */cgi-bin/leds* api)

## Upcoming features
- Multi-language (partial)
- Manage TTS cache
- Display snapshots (partial)
- Webcam (Using */cgi-bin/webcam* api)
- Radios (Using */cgi-bin/sound?url={karotzStreamUrl}* and */cgi-bin/sound_control?cmd={cmd}* apis)
- Disable ears
- RFID Management??? Not sure yet.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the "+" button
4. Search for "OpenKarotz"
5. Install the integration
6. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub](https://github.com/phschott/HA_openkarotz/releases)
2. Extract the `custom_components/openkarotz` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration
Just enter IP or hostname or your Karrotz. Done!

## Karotz Camera
Use standard "MJPEG IP Camera" integration and use URL MJPEG: http://{karotz_IP}/cgi-bin/webcam
You can also configure still image: http://{karotz_IP}/cgi-bin/snapshot_view?silent=1

## Known issues
- Default light color and pulse is not synced from status

# Recommanded link
[Free Rabbits](https://www.freerabbits.nl)
[Nabaztag/Karotz Documentation](https://docs.nabaztag.com)