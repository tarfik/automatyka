import urequests
import os
import machine

VERSION_URL = "https://raw.githubusercontent.com/tarfik/automatyka/main/version.json"

class OTA:
    def __init__(self):
        self.current_version = "1"

    def update(self):
        try:
            r = urequests.get(VERSION_URL)
            data = r.json()
            r.close()

            if data["version"] == self.current_version:
                return

            for file in data["files"]:
                self.download(file)

            machine.reset()

        except Exception as e:
            print("OTA error:", e)

    def download(self, filename):
        url = f"https://raw.githubusercontent.com/USER/REPO/main/{filename}"
        r = urequests.get(url)

        with open(filename, "w") as f:
            f.write(r.text)

        r.close()
