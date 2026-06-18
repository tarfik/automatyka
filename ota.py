import urequests
import os
import machine


GITHUB_URL = "https://raw.githubusercontent.com/tarfik/automatyka/refs/heads/main/"


class OTA:
    def __init__(self):
        self.current_version = "1"

    def update(self):
        try:
            r = urequests.get(GITHUB_URL+"version.json")
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
        url = GITHUB_URL+filename
        r = urequests.get(url)

        with open(filename, "w") as f:
            f.write(r.text)

        r.close()
