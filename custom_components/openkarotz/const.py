DOMAIN = "openkarotz"
MANUFACTURER = "Karotz"
MODEL = "OpenKarotz"
FILENAME = "SelectedKarotzPicture.jpg"
DEFAULT_NAME = "OpenKarotz Picture"
# --- Snapshot image integration ---

# Entity ID du select qui liste les snapshots disponibles sur le Karotz
SNAPSHOT_SELECT_ENTITY = "select.openkarotz_snapshots"

# Template d'URL pour télécharger un snapshot.
# {host}     → adresse IP ou hostname du Karotz (ex: "192.168.1.170")
# {filename} → valeur courante du select        (ex: "snapshot_2026_05_15_12_31_00.jpg")
SNAPSHOT_URL_TEMPLATE = "http://{host}/cgi-bin/snapshot_get?filename={filename}"
