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
- Multi-language
- Manage TTS cache
- Display snapshots
- Webcam (Using */cgi-bin/webcam* api)
- Radios (Using */cgi-bin/sound?url={karotzStreamUrl}* and */cgi-bin/sound_control?cmd={cmd}* apis)
- Disable ears
- RFID Management??? Not sure yet.

## Known issues
- Pulse light is not working
- Default light color and pulse is not synced from status
- Number of snapshots not refreshed after snaphot or cleanup (1' delay)