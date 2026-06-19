import urequests
import os
import machine
import ujson


GITHUB_URL = "https://raw.githubusercontent.com/tarfik/automatyka/refs/heads/main/"


class OTA:
    def __init__(self):
        self.current_version = self._load_current_version()

    def _load_current_version(self):
        try:
            with open("version.json", "r") as f:
                data = ujson.loads(f.read())
                return str(data.get("version", "0"))
        except Exception:
            return "0"

    def _is_valid_filename(self, filename):
        if not filename:
            return False
        if "/" in filename or "\\" in filename:
            return False
        if filename.startswith("."):
            return False
        return True

    def _write_atomic(self, filename, content):
        tmp_name = filename + ".tmp"
        with open(tmp_name, "w") as f:
            f.write(content)

        try:
            os.remove(filename)
        except Exception:
            pass

        os.rename(tmp_name, filename)

    def _get_json(self, url):
        r = None
        try:
            r = urequests.get(url)
            if r.status_code != 200:
                raise Exception("HTTP {} for {}".format(r.status_code, url))
            return r.json()
        finally:
            if r is not None:
                r.close()

    def _get_text(self, url):
        r = None
        try:
            r = urequests.get(url)
            if r.status_code != 200:
                raise Exception("HTTP {} for {}".format(r.status_code, url))
            return r.text
        finally:
            if r is not None:
                r.close()

    def update(self):
        try:
            data = self._get_json(GITHUB_URL + "version.json")
            remote_version = str(data.get("version", "0"))
            files = data.get("files", [])

            if not isinstance(files, list):
                raise Exception("Invalid files list in version.json")

            if remote_version == self.current_version:
                print("OTA: already up to date")
                return

            for file in files:
                self.download(file)

            self._write_atomic("version.json", ujson.dumps(data))
            self.current_version = remote_version

            machine.reset()

        except Exception as e:
            print("OTA error:", e)

    def download(self, filename):
        if not self._is_valid_filename(filename):
            raise Exception("Invalid filename: {}".format(filename))

        url = GITHUB_URL + filename
        content = self._get_text(url)
        self._write_atomic(filename, content)
