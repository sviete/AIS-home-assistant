# -*- coding: utf-8 -*-
"""
Support for AIS AudioBooks

For more details about this component, please refer to the documentation at
https://ai-speaker.com
"""
import asyncio
import logging
import requests
import json
import os.path
from homeassistant.components import ais_cloud
from homeassistant.ais_dom import ais_global
aisCloud = ais_cloud.AisCloudWS()

DOMAIN = 'ais_audiobooks_service'
PERSISTENCE_AUDIOBOOKS = '/.dom/audiobboks.json'
_LOGGER = logging.getLogger(__name__)
AUDIOBOOKS_WS_URL = 'https://wolnelektury.pl/api/audiobooks/?format=json'


@asyncio.coroutine
def async_setup(hass, config):
    """Register the service."""
    config = config.get(DOMAIN, {})

    _LOGGER.info("Initialize the authors list.")
    data = hass.data[DOMAIN] = AudioBooksData(hass, config)
    yield from data.async_load_all_books()

    # register services
    def get_books(call):
        _LOGGER.info("get_books")
        data.get_books(call)

    def get_chapters(call):
        _LOGGER.info("get_chapters")
        data.get_chapters(call)

    def select_chapter(call):
        _LOGGER.info("select_chapter")
        data.select_chapter(call)

    hass.services.async_register(
        DOMAIN, 'get_books', get_books)
    hass.services.async_register(
        DOMAIN, 'get_chapters', get_chapters)
    hass.services.async_register(
        DOMAIN, 'select_chapter', select_chapter)

    return True


class AudioBooksData:
    """Class to hold audiobooks data."""

    def __init__(self, hass, config):
        """Initialize the books authors."""
        self.hass = hass
        self.all_books = []

    def get_books(self, call):
        """Load books for the selected author."""
        if "author" not in call.data:
            _LOGGER.error("No author")
            return []

        if call.data["author"] == ais_global.G_EMPTY_OPTION:
            # reset status for item below
            self.hass.states.async_set("sensor.audiobookslist", -1, {})
            self.hass.states.async_set("sensor.audiobookschapterslist", -1, {})
            return

        list_info = {}
        list_idx = 0
        for item in self.all_books:
            if item["author"] == call.data["author"]:
                list_info[list_idx] = {}
                try:
                    list_info[list_idx]["thumbnail"] = "https://wolnelektury.pl/media/" + item["cover_thumb"]
                except Exception:
                    list_info[list_idx]["thumbnail"] = item["simple_thumb"]
                list_info[list_idx]["title"] = item["title"]
                list_info[list_idx]["name"] = item["title"]
                list_info[list_idx]["uri"] = item["url"]
                list_info[list_idx]["media_source"] = ais_global.G_AN_AUDIOBOOK
                list_info[list_idx]["audio_type"] = ais_global.G_AN_AUDIOBOOK
                list_info[list_idx]["icon"] = "mdi:book-play"
                list_info[list_idx]["lookup_url"] = item["href"]
                list_info[list_idx]["lookup_name"] = item["title"]
                list_idx = list_idx + 1

        self.hass.states.async_set("sensor.audiobookslist", 0, list_info)
        self.hass.services.call('ais_audiobooks_service', 'get_chapters', {"id": 0})

        import homeassistant.components.ais_ai_service as ais_ai
        if ais_ai.CURR_ENTITIE == 'input_select.book_autor':
            ais_ai.set_curr_entity(self.hass, 'sensor.audiobookslist')
            self.hass.services.call('ais_ai_service', 'say_it', {"text": "Wybierz książkę"})

    def get_chapters(self, call):
        """Load chapters for the selected book."""
        if "id" not in call.data:
            _LOGGER.error("No book id")
            return

        state = self.hass.states.get("sensor.audiobookslist")
        attr = state.attributes
        track = attr.get(int(call.data['id']))
        self.hass.states.async_set("sensor.audiobookslist", call.data['id'], attr)

        try:
            ws_resp = requests.get(track["lookup_url"] + "?format=json", timeout=10)
            data = ws_resp.json()

        except Exception as e:
            _LOGGER.error("Can't load chapters: " + str(e))
            self.hass.services.call('ais_ai_service', 'say_it', {"text": "Nie można pobrać rozdziałów"})
            return

        list_info = {}
        list_idx = 0
        for item in data["media"]:
            if item["type"] == "ogg":
                list_info[list_idx] = {}
                try:
                    list_info[list_idx]["thumbnail"] = data["cover"]
                except Exception:
                    list_info[list_idx]["thumbnail"] = data["simple_cover"]
                list_info[list_idx]["title"] = item["name"]
                list_info[list_idx]["name"] = item["name"]
                list_info[list_idx]["uri"] = item["url"]
                list_info[list_idx]["media_source"] = ais_global.G_AN_AUDIOBOOK_CHAPTER
                list_info[list_idx]["audio_type"] = ais_global.G_AN_AUDIOBOOK_CHAPTER
                list_info[list_idx]["icon"] = 'mdi:play'
                list_idx = list_idx + 1

        self.hass.states.async_set("sensor.audiobookschapterslist", 0, list_info)
        self.hass.services.call('ais_audiobooks_service', 'select_chapter', {"id": 0})

        # check if the change was done form remote
        import homeassistant.components.ais_ai_service as ais_ai
        if ais_ai.CURR_ENTITIE == 'sensor.audiobookslist':
            ais_ai.set_curr_entity(self.hass, 'sensor.audiobookschapterslist')
            self.hass.services.call('ais_ai_service', 'say_it', {"text": "Włączam pierwszy rozdział"})

    def select_chapter(self, call):
        """Get chapter stream url for the selected name."""
        if "id" not in call.data:
            _LOGGER.error("No book chapter id")
            return

        state = self.hass.states.get("sensor.audiobookschapterslist")
        attr = state.attributes
        track = attr.get(int(call.data['id']))
        self.hass.states.async_set("sensor.audiobookschapterslist", call.data['id'], attr)

        # set stream uri, image and title
        _audio_info = json.dumps(
            {"IMAGE_URL": track["thumbnail"], "NAME": track["title"], "MEDIA_SOURCE": ais_global.G_AN_AUDIOBOOK,
             "media_content_id": track["uri"]})
        self.hass.services.call('media_player', 'play_media',
                                {"entity_id": ais_global.G_LOCAL_EXO_PLAYER_ENTITY_ID,
                                 "media_content_type": "ais_content_info",
                                 "media_content_id": _audio_info})

    @asyncio.coroutine
    def async_load_all_books(self):
        """Load all the books and cache the JSON."""

        def load():
            """Load the items synchronously."""
            path = self.hass.config.path() + PERSISTENCE_AUDIOBOOKS
            try:
                ws_resp = requests.get(AUDIOBOOKS_WS_URL, timeout=10)
                data = ws_resp.json()
                with open(path, 'w+') as my_file:
                    json.dump(data, my_file)
            except Exception as e:
                _LOGGER.info("Can't load books list: " + str(e))

            if not os.path.isfile(path):
                return

            with open(path) as file:
                self.all_books = json.loads(file.read())

            #  TODO data validation
            # self.all_books =
            # for book in books:
            #     b = {}
            #     self.all_books.append(b)

            authors = [ais_global.G_EMPTY_OPTION]
            for item in self.all_books:
                if item["author"] not in authors:
                    authors.append(item["author"])
            self.hass.services.call(
                'input_select',
                'set_options', {
                    "entity_id": "input_select.book_autor",
                    "options": sorted(authors)})

        yield from self.hass.async_add_job(load)
