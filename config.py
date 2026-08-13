# File: lib/kernel/config.py

from configparser import ConfigParser
import urllib.request
import urllib.error
import time
import logging

logger = logging.getLogger('gunicorn.error')

class AutoReloadConfigParser(dict):
    def __init__(self, config_file="config.ini", ttl_seconds=1200):
        super().__init__()
        self.config_file = "/etc/%s" % config_file
        self.ttl_seconds = ttl_seconds
        self.last_loaded = 0
        self._parser = ConfigParser()

    def read_with_includes(self):
        temp_parser = ConfigParser()
        temp_parser.optionxform = str
        try:
            read_files = temp_parser.read(self.config_file, encoding="utf-8")
            if not read_files:
                raise FileNotFoundError(f"Config file '{self.config_file}' " \
                                         "not found")

            if temp_parser.has_section("include"):
                urls_raw = temp_parser.get("include", "urls", fallback="")
                urls = [u.strip() for u in urls_raw.splitlines() if u.strip()]
                temp_parser.remove_section("include")

                for url in urls:
                    self._load_from_url(temp_parser, url)

            self._parser = temp_parser

            self.clear()


            for section in temp_parser.sections():
                section_data = {}
                for key, val in temp_parser[section].items():
                    if isinstance(val, str):
                        cleanval = val.strip().strip('"\'')
                    else:
                        cleanval = val
                    section_data[key] = cleanval

                self[section] = section_data

            self.last_loaded = time.time()
            logger.info("Config successfuly loaded")

        except Exception as e:
            logger.warning(f"Config load failed: {e}. " \
                            "using old.")
            if self.last_loaded == 0:
                raise e

    def _load_from_url(self, target_parser, url: str):
        req = urllib.request.Request(url, headers={
              'User-Agent': 'Python-ConfigParser'})
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read().decode("utf-8")
            target_parser.read_string(content, source=url)

    def _check_ttl(self):
       if time.time() - self.last_loaded > self.ttl_seconds:
           self.read_with_includes()

    def get(self, section, option, fallback=None):
       self._check_ttl()
       return self._parser.get(section, option, fallback=fallback)

    def getint(self, section, option, fallback=None):
       self._check_ttl()
       return self._parser.getint(section, option, fallback=fallback)

    def getboolean(self, section, option, fallback=None):
       self._check_ttl()
       return self._parser.getboolean(section, option, fallback=fallback)

    def __getitem__(self, key):
        self._check_ttl()
        return super().__getitem__(key)

    def get(self, key, default=None):
        self._check_ttl()
        return super().get(key, default)

    def __iter__(self):
        self._check_ttl()
        return super().__iter__()

    def items(self):
        self._check_ttl()
        return super().items()

    def values(self):
        self._check_ttl()
        return super().values()




# Singleton-Instanz erzeugen
config = AutoReloadConfigParser(config_file="SNowRepl.env", ttl_seconds=30)
config.read_with_includes()


