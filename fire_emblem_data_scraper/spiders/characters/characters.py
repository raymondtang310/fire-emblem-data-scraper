# -*- coding: utf-8 -*-
from collections import OrderedDict
from string import Template

import scrapy
from bs4 import BeautifulSoup

from fire_emblem_data_scraper.constants import MAX_NUM_OTHER_IMAGES
from fire_emblem_data_scraper.spiders.characters.character_item import CharacterItem


class CharactersSpider(scrapy.Spider):
    """
    CharactersSpider is a Spider that scrapes data on Fire Emblem characters.
    """
    name = 'characters'
    start_urls = ['https://fireemblemwiki.org/wiki/Category:Characters']
    custom_settings = {
        'MONGO_COLLECTION_NAME': 'characters'
    }

    BASE_URL = 'https://fireemblemwiki.org'

    def parse(self, response):
        """
        Parses the current web page being crawled.

        :param response: The Response of the current web page being crawled
        :type response: scrapy.http.Response
        :return: A generator of Requests
        :rtype: generator<scrapy.http.Request>
        """
        character_links = response.xpath('//div[@id="mw-pages"]//div[@class="mw-category-group"]//li//a/@href').getall()
        next_page_link = response.xpath('//div[@id="mw-pages"]//a[contains(text(), "next")]/@href').get()

        for character_link in character_links:
            character_url = self.BASE_URL + character_link
            yield scrapy.Request(character_url, callback=self.parse_character)

        if next_page_link:
            next_page_url = self.BASE_URL + next_page_link
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_character(self, response):
        """
        Parses the current web page being crawled into a CharacterItem.

        :param response: The Response of the current web page being crawled
        :type response: scrapy.http.Response
        :return: A CharacterItem encapsulating data on a Fire Emblem character that was scraped from the current web
                 page being crawled
        :rtype: CharacterItem
        """
        character_item = CharacterItem()

        is_name_parsed = self.__parse_name(response, character_item)
        if not is_name_parsed:
            return None

        self.__parse_images(response, character_item)
        self.__parse_appearances(response, character_item)
        self.__parse_titles(response, character_item)
        self.__parse_voice_actors(response, character_item)

        return character_item

    def __parse_name(self, response, character_item):
        """
        Parses the name of the Fire Emblem character.

        :param response: The Response of the current web page being crawled
        :type response: scrapy.http.Response
        :param character_item: The CharacterItem to hold the name
        :type character_item: CharacterItem
        :return: True if the name of the Fire Emblem character was found, False otherwise
        :rtype: Boolean
        """
        name = response.xpath('//h1[@id="firstHeading"]/text()').get()

        if name:
            character_item['name'] = name
            return True

        return False

    def __parse_images(self, response, character_item):
        """
        Parses the images of the Fire Emblem character.

        :param response: The Response of the current web page being crawled
        :type response: scrapy.http.Response
        :param character_item: The CharacterItem to hold the images
        :type character_item: CharacterItem
        :return: None
        """
        image_path = (f'//a[@class="image"]//img[contains(@src, "{character_item["name"]}") or '
                      f'contains(@src, "{character_item["name"].lower()}")]/@src')
        primary_image_link = response.xpath(
            f'//div[@class="tab_content" and @style="display:block;"]{image_path}').get()
        image_links = list(OrderedDict.fromkeys(response.xpath(image_path).getall()))  # remove duplicate images

        if not primary_image_link and image_links:
            primary_image_link = image_links[0]
        if primary_image_link:
            image_links.remove(primary_image_link)

        if primary_image_link:
            character_item['primaryImage'] = self.BASE_URL + primary_image_link
        if image_links:
            image_urls = [self.BASE_URL + image_link for image_link in image_links[:MAX_NUM_OTHER_IMAGES]]
            character_item['otherImages'] = image_urls

    def __parse_appearances(self, response, character_item):
        """
        Parses the appearances of the Fire Emblem character.

        :param response: The Response of the current web page being crawled
        :type response: scrapy.http.Response
        :param character_item: The CharacterItem to hold the appearances
        :type character_item: CharacterItem
        :return: None
        """
        appearances = response.xpath('//tr[th[contains(text(), "Appearance")]]/td//a/@title').getall()

        if appearances:
            character_item['appearances'] = appearances

    def __parse_titles(self, response, character_item):
        """
        Parses the titles of the Fire Emblem character.

        :param response: The Response of the current web page being crawled
        :type response: scrapy.http.Response
        :param character_item: The CharacterItem to hold the titles
        :type character_item: CharacterItem
        :return: None
        """
        titles = []
        title_htmls = response.xpath('//tr[th[contains(text(), "Title")]]/td//li').getall() or response.xpath(
            '//tr[th[contains(text(), "Title")]]/td/p').getall()
        for title_html in title_htmls:
            title = BeautifulSoup(title_html, 'html.parser').get_text()
            if title:
                titles.append(title)

        if titles:
            character_item['titles'] = titles

    def __parse_voice_actors(self, response, character_item):
        """
        Parses the voice actors of the Fire Emblem character.

        :param response: The Response of the current web page being crawled
        :type response: scrapy.http.Response
        :param character_item: The CharacterItem to hold the voice actors
        :type character_item: CharacterItem
        :return: None
        """
        voice_actor_path_template = Template(
            '//tr[th[contains(text(), "Voice")]]/td//a[following-sibling::small/text()[contains(., "$language")]]'
            '/text()')
        english_voice_actors = response.xpath(voice_actor_path_template.substitute(language='English')).getall()
        japanese_voice_actors = response.xpath(voice_actor_path_template.substitute(language='Japanese')).getall()

        voice_actors = {}
        if english_voice_actors:
            voice_actors['english'] = english_voice_actors
        if japanese_voice_actors:
            voice_actors['japanese'] = japanese_voice_actors

        if voice_actors:
            character_item['voiceActors'] = voice_actors
