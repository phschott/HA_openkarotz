# OpenKarotz — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/phschott/HA_openkarotz.svg)](https://github.com/phschott/HA_openkarotz/releases)
[![GitHub license](https://img.shields.io/github/license/phschott/HA_openkarotz.svg)](LICENSE)
[![HA community](https://img.shields.io/badge/community-Home%20Assistant-blue.svg)](https://community.home-assistant.io)

Control your [Nabaztag/Karotz](https://docs.nabaztag.com) rabbit from Home Assistant using the [OpenKarotz](https://www.freerabbits.nl) firmware. This integration communicates locally over HTTP — no cloud required.

> **Prerequisite:** OpenKarotz (Free Rabbits OS) must be installed and running on your rabbit before using this integration.

---

## Features

- **Live status sync** — LED color, pulse mode, and diagnostic sensors refresh every 10 seconds
- **Full LED control** — set primary and secondary RGB colors, enable/disable pulse, adjust pulse speed
- **Ear control** — position each ear independently (0–16) or trigger a random movement
- **Text-to-speech** — type text, pick a voice, and make your rabbit speak
- **Moods** — trigger any of the 300+ built-in mood animations
- **Snapshots** — take, browse, and display photos from the rabbit's camera
- **Radio** — select and play internet radio streams
- **Power management** — wake up, put to sleep, or reboot the device

---

## Installation

### HACS (Recommended)

1. Open **HACS** in Home Assistant
2. Go to **Integrations**
3. Click the **Explore & Download Repositories** button
4. Search for **OpenKarotz** and select it
5. Click **Download**
6. Restart Home Assistant

### Manual

1. Download the [latest release](https://github.com/phschott/HA_openkarotz/releases)
2. Copy the `custom_components/openkarotz` folder into your Home Assistant `custom_components` directory
3. Restart Home Assistant

---

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **OpenKarotz**
3. Enter the IP address or hostname of your rabbit
4. Click **Submit**

The integration will auto-discover all entities and group them into devices.

---

## Devices & Entities

The integration creates five logical devices, each grouping related entities.

### OpenKarotz

The main device exposing global status and power controls.

| Entity | Platform | Description |
|---|---|---|
| Wake up | Button | Wake the rabbit from sleep |
| Sleep | Button | Put the rabbit to sleep |
| Reboot | Button | Reboot the device *(config category)* |
| Version | Sensor | Firmware version *(diagnostic)* |
| Used space | Sensor | Internal storage usage in % *(diagnostic)* |
| WLAN MAC | Sensor | Wi-Fi MAC address *(diagnostic)* |
| Tags | Sensor | Number of registered RFID tags |
| Moods | Sensor | Number of available moods |
| Sounds | Sensor | Number of available sounds |
| Stories | Sensor | Number of available stories |

### OpenKarotz Ears

| Entity | Platform | Description |
|---|---|---|
| Ear left | Number | Left ear position (0–16, slider) |
| Ear right | Number | Right ear position (0–16, slider) |
| Random ears | Button | Move ears to a random position |
| Reset ears | Button | Reset ears to default position *(config category)* |

### OpenKarotz LEDs

LED state is read from the device every 10 seconds and synced automatically.

| Entity | Platform | Description |
|---|---|---|
| Color 1 | Light | Primary LED color (RGB) |
| Color 2 | Light | Secondary LED color used during pulse (RGB) |
| LED pulse | Switch | Enable/disable pulsing animation |
| Pulse speed | Number | Animation speed (0–2000, slider) |
| Turn off LEDs | Button | Turn off all LEDs immediately |
| LED color | Sensor | Current hex color reported by device *(diagnostic)* |
| LED pulse | Sensor | Current pulse state reported by device *(diagnostic)* |

### OpenKarotz Sound

| Entity | Platform | Description |
|---|---|---|
| Voice | Select | Select a TTS voice |
| TTS text | Text | Text to speak |
| Speak | Button | Speak the TTS text with the selected voice |
| Mood | Select | Select a mood animation |
| Play mood | Button | Play the selected mood |
| Random mood | Button | Play a random mood |
| Play clock | Button | Display the clock animation |
| Radios | Select | Select an internet radio stream |

### OpenKarotz Picture

| Entity | Platform | Description |
|---|---|---|
| Snapshot | Button | Take a photo |
| Clear snapshots | Button | Delete all snapshots *(config category)* |
| Snapshots | Select | Browse available snapshots |
| Snapshot count | Sensor | Number of stored snapshots |
| Snapshot viewer | Image | Display the selected snapshot |

---

## Camera

The rabbit's webcam is not exposed as a native entity. Use Home Assistant's built-in **MJPEG IP Camera** integration:

- **MJPEG URL:** `http://<karotz_ip>/cgi-bin/webcam`
- **Still image URL:** `http://<karotz_ip>/cgi-bin/snapshot_view?silent=1`

---

## Update Intervals

| Data | Interval |
|---|---|
| Status (LED, sensors) | 10 seconds |
| Snapshots | 10 seconds |
| Voices, moods, radios | 4 hours |

---

## Automation Blueprints

Five blueprints are included and appear directly in **Settings → Automations → Blueprints** after installation.

| Blueprint | Description |
|---|---|
| **Daily Schedule** | Wake up and put the rabbit to sleep at fixed times |
| **LED Color on State** | Change LED color when an entity reaches a specific state |
| **Announce on Trigger** | Speak a TTS message when something happens |
| **Play Sound on Trigger** | Play a local sound when something happens |
| **Radio Schedule** | Start and stop a radio station at scheduled times |
| **LED on Persistent Notifications** | Green = no notifications, Red = at least one active |

### Installing a blueprint

1. Go to **Settings → Automations → Blueprints**
2. Find the OpenKarotz blueprint you want
3. Click **Create Automation**
4. Fill in the fields and save

### Understanding the "Trigger state" field

Several blueprints (**LED Color on State**, **Announce on Trigger**, **Play Sound on Trigger**) ask for a **Trigger entity** and a **Trigger state**. The automation fires when the entity's state equals that value exactly.

**Binary states** — use the raw HA state string:

| Situation | Trigger state |
|---|---|
| A switch / light turns on | `on` |
| A switch / light turns off | `off` |
| A person arrives home | `home` |
| A person leaves | `not_home` |
| A door sensor opens | `open` |
| An alarm is armed | `armed_away` |

**Numeric sensors** — enter the exact number as a string. This only matches that precise value, which is rarely what you want for a sensor:

| Situation | Trigger state |
|---|---|
| Temperature equals 21 | `21` |
| Battery equals 10 % | `10` |

For numeric comparisons (**greater than**, **less than**, **above a threshold**), the Trigger state field is not sufficient on its own. Use a **Template sensor** helper instead:

1. Go to **Settings → Devices & Services → Helpers → Create helper → Template**
2. Create a binary sensor with a template such as:

```jinja2
{{ states('sensor.temperature_living_room') | float > 25 }}
```

3. Use that helper as the **Trigger entity** and set **Trigger state** to `on` (true) or `off` (false).

**Examples of template helpers for numeric thresholds:**

| Goal | Template |
|---|---|
| Temperature above 25 °C | `{{ states('sensor.temperature') \| float > 25 }}` |
| Temperature below 18 °C | `{{ states('sensor.temperature') \| float < 18 }}` |
| Battery below 20 % | `{{ states('sensor.battery') \| int < 20 }}` |
| More than 3 people home | `{{ states('zone.home') \| int > 3 }}` |

---

## Roadmap

- [ ] Multi-language support
- [ ] TTS cache management
- [ ] Media player entity for radio playback control (play/pause/stop)
- [ ] Ears disabled toggle
- [ ] RFID tag management

---

## Links

- [Free Rabbits — OpenKarotz firmware](https://www.freerabbits.nl)
- [Nabaztag/Karotz API documentation](https://docs.nabaztag.com)
- [Report an issue](https://github.com/phschott/HA_openkarotz/issues)
