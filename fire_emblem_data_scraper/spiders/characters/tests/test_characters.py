import unittest
from unittest.mock import patch

from scrapy.http import HtmlResponse

from fire_emblem_data_scraper.spiders.characters.characters import CharactersSpider


class TestCharactersSpider(unittest.TestCase):
    """
    TestCharactersSpider is a class for unit testing CharactersSpider.
    """

    def setUp(self):
        """
        Method that executes before each test method.

        :return: None
        """
        self.spider = CharactersSpider()

    @patch('fire_emblem_data_scraper.spiders.characters.characters.scrapy.Request')
    def test_when_parsing_response_then_request_is_made_for_each_character_link(self, request_mock):
        """
        Tests that a request is made for each link to a Fire Emblem character web page that is found in the given
        response when parsing the given response.

        :param request_mock: A mock of scrapy.Request
        :type request_mock: MagicMock
        :return: None
        """
        character_links = ['/Byleth', '/Edelgard']
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Fire Emblem Characters</title>
                </head>
                <body>
                    <div id="mw-pages">
                        <div class="mw-category-group">
                            <ul>
                                <li>
                                    <a href="{character_links[0]}"></a>
                                </li>
                                <li>
                                    <a href="{character_links[1]}"></a>
                                </li>
                            </ul>
                        </div>
                    </div>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        requests = self.spider.parse(response)

        for character_link, request in zip(character_links, requests):
            character_url = self.spider.BASE_URL + character_link
            request_mock.assert_called_with(character_url, callback=self.spider.parse_character)

    @patch('fire_emblem_data_scraper.spiders.characters.characters.scrapy.Request')
    def test_when_parsing_response_given_next_page_link_is_found_then_request_is_made_for_next_page(self, request_mock):
        """
        Tests that a request is made for the next page when parsing the given response, given that a link for the next
        page is found in the given response.

        :param request_mock: A mock of scrapy.Request
        :type request_mock: MagicMock
        :return: None
        """
        next_page_link = '/next-page'
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Fire Emblem Characters</title>
                </head>
                <body>
                    <div id="mw-pages">
                        <a href="{next_page_link}">next page</a>
                    </div>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))
        next_page_url = self.spider.BASE_URL + next_page_link

        requests = self.spider.parse(response)

        for _ in requests:
            request_mock.assert_called_with(next_page_url, callback=self.spider.parse)

    @patch('fire_emblem_data_scraper.spiders.characters.characters.scrapy.Request')
    def test_when_parsing_response_given_next_page_link_is_not_found_then_request_is_not_made_for_next_page(
            self, request_mock):
        """
        Tests that a request is not made for the next page when parsing the given response, given that a link for the
        next page is not found in the given response.

        :param request_mock: A mock of scrapy.Request
        :type request_mock: MagicMock
        :return: None
        """
        html = '''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Fire Emblem Characters</title>
                </head>
                <body>
                    <div id="mw-pages"></div>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        requests = self.spider.parse(response)

        for _ in requests:
            request_mock.assert_not_called()

    def test_when_parsing_character_given_name_is_found_then_name_is_scraped(self):
        """
        Tests that the name of the Fire Emblem character is scraped when parsing the given response of the character's
        web page, given that the name of the character is found in the given response.

        :return: None
        """
        name = 'Lucina'
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Lucina</title>
                </head>
                <body>
                    <h1 id="firstHeading">{name}</h1>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertEqual(character_item['name'], name, 'Name was not scraped correctly')

    def test_when_parsing_character_given_name_is_not_found_then_character_is_not_scraped(self):
        """
        Tests that a Fire Emblem character item is not scraped when parsing the given response of the character's web
        page, given that the name of the Fire Emblem character is not found in the given response.

        :return: None
        """
        html = '''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title></title>
                </head>
                <body>
                    <h1 id="firstHeading"></h1>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        result = self.spider.parse_character(response)

        self.assertIsNone(result, 'An item was unexpectedly scraped')

    def test_when_parsing_character_given_primary_image_is_found_then_images_are_scraped(self):
        """
        Tests that images of the Fire Emblem character are scraped correctly when parsing the given response of the
        character's web page, given that a primary image is found in the given response. In this scenario, images are
        scraped correctly if the primary image found is scraped as the primary image and other images found are scraped
        as other images.

        :return: None
        """
        primary_image_link = '/path-of-radiance-ike.png'
        other_image_links = ['/radiant-dawn-ike.jpg', '/fire-emblem-heroes-ike.jpg']
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Ike</title>
                </head>
                <body>
                    <h1 id="firstHeading">Ike</h1>
                    <div class="tab_content" style="display:block;">
                        <a class="image">
                            <img src="{primary_image_link}">
                        </a>
                    </div>
                    <div class="tab_content" style="display:none;">
                        <a class="image">
                            <img src="{other_image_links[0]}">
                        </a>
                    </div>
                    <div class="tab_content" style="display:none;">
                        <a class="image">
                            <img src="{other_image_links[1]}">
                        </a>
                    </div>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))
        primary_image_url = self.spider.BASE_URL + primary_image_link
        other_images_urls = [self.spider.BASE_URL + other_image_link for other_image_link in other_image_links]

        character_item = self.spider.parse_character(response)

        self.assertEqual(character_item['primaryImage'], primary_image_url, 'Primary image was not scraped correctly')
        self.assertEqual(character_item['otherImages'], other_images_urls, 'Other images were not scraped correctly')

    def test_when_parsing_character_given_primary_image_is_not_found_and_other_images_are_found_then_images_are_scraped_with_first_image_found_as_primary_image(
            self):
        """
        Tests that images of the Fire Emblem character are scraped correctly when parsing the given response of the
        character's web page, given that a primary image cannot be found in the given response but other images are
        found. In this scenario, images are scraped correctly if the first image found is scraped as the primary image
        and other images found are scraped as other images.

        :return: None
        """
        image_links = ['/thracia776-reinhardt.jpg', '/fire-emblem-heroes-reinhardt.jpg']
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Reinhardt</title>
                </head>
                <body>
                    <h1 id="firstHeading">Reinhardt</h1>
                    <div>
                        <a class="image">
                            <img src="{image_links[0]}">
                        </a>
                    </div>
                    <div>
                        <a class="image">
                            <img src="{image_links[1]}">
                        </a>
                    </div>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))
        primary_image_url = self.spider.BASE_URL + image_links[0]
        other_images_urls = [self.spider.BASE_URL + image_links[1]]

        character_item = self.spider.parse_character(response)

        self.assertEqual(character_item['primaryImage'], primary_image_url, 'Primary image was not scraped correctly')
        self.assertEqual(character_item['otherImages'], other_images_urls, 'Other images were not scraped correctly')

    def test_when_parsing_character_given_images_are_not_found_then_images_are_not_scraped(self):
        """
        Tests that images of the Fire Emblem character are not scraped when parsing the given response of the
        character's web page, given that images of the Fire Emblem character are not found in the given response.

        :return: None
        """
        html = '''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Altina</title>
                </head>
                <body>
                    <h1 id="firstHeading">Altina</h1>
                    <div>No images of Altina!</div>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertNotIn('primaryImage', character_item, 'Primary image was unexpectedly scraped')
        self.assertNotIn('otherImages', character_item, 'Other images were unexpectedly scraped')

    def test_when_parsing_character_given_appearances_are_found_then_appearances_are_scraped(self):
        """
        Tests that appearances of the Fire Emblem character are scraped when parsing the given response of the
        character's web page, given that the character's appearances are found in the given response.

        :return: None
        """
        appearances = ['Fire Emblem: Three Houses', 'Fire Emblem: Heroes', 'Super Smash Bros. Ultimate']
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Byleth</title>
                </head>
                <body>
                    <h1 id="firstHeading">Byleth</h1>
                    <table>
                        <tr>
                            <th>Appearances</th>
                            <td>
                                <ul>
                                    <li>
                                        <a href="/wiki/Fire_Emblem:_Three_Houses" title="{appearances[0]}">
                                            Three Houses
                                        </a>
                                    </li>
                                    <li>
                                        <a href="/wiki/Fire_Emblem:_Heroes" title="{appearances[1]}">Heroes</a>
                                    </li>
                                    <li>
                                        <a href="/wiki/Super_Smash_Bros._Ultimate" title="{appearances[2]}">
                                            Super Smash Bros. Ultimate
                                        </a>
                                    </li>
                                </ul>
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertEqual(character_item['appearances'], appearances, 'Appearances were not scraped correctly')

    def test_when_parsing_character_given_appearances_are_not_found_then_appearances_are_not_scraped(self):
        """
        Tests that appearances of the Fire Emblem character are not scraped when parsing the given response of the
        character's web page, given that the character's appearances are not found in the given response.

        :return: None
        """
        html = '''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Byleth</title>
                </head>
                <body>
                    <h1 id="firstHeading">Byleth</h1>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertNotIn('appearances', character_item, 'Appearances were unexpectedly scraped')

    def test_when_parsing_character_given_multiple_titles_are_found_then_titles_are_scraped(self):
        """
        Tests that titles of the Fire Emblem character are scraped when parsing the given response of the character's
        web page, given that multiple titles for the character are found in the given response.

        :return: None
        """
        titles = ['Prince of Light', 'Hero-King']
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Marth</title>
                </head>
                <body>
                    <h1 id="firstHeading">Marth</h1>
                    <table>
                        <tr>
                            <th>Title(s)</th>
                            <td>
                                <ul>
                                    <li>{titles[0]}</li>
                                    <li>{titles[1]}</li>
                                </ul>
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertEqual(character_item['titles'], titles, 'Titles were not scraped correctly')

    def test_when_parsing_character_given_title_text_is_split_amongst_multiple_elements_then_titles_are_scraped(self):
        """
        Tests that titles of the Fire Emblem character are scraped when parsing the given response of the character's
        web page, given that the text of a title of the character is split amongst multiple elements in the given
        response.

        :return: None
        """
        first_title_partition = 'Prince of '
        second_title_partition = 'Altea'
        titles = [first_title_partition + second_title_partition]
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Ike</title>
                </head>
                <body>
                    <h1 id="firstHeading">Ike</h1>
                    <table>
                        <tr>
                            <th>Title(s)</th>
                            <td>
                                <ul>
                                    <li>{first_title_partition}<a href="/wiki/Altea">{second_title_partition}</a></li>
                                </ul>
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertEqual(character_item['titles'], titles, 'Titles were not scraped correctly')

    def test_when_parsing_character_given_one_title_is_found_then_title_is_scraped(self):
        """
        Tests that the title of the Fire Emblem character is scraped when parsing the given response of the character's
        web page, given that only one title for the character is found in the given response.

        :return: None
        """
        titles = ['Radiant Hero']
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Ike</title>
                </head>
                <body>
                    <h1 id="firstHeading">Ike</h1>
                    <table>
                        <tr>
                            <th>Title(s)</th>
                            <td>
                                <p>{titles[0]}</p>
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertEqual(character_item['titles'], titles, 'Titles were not scraped correctly')

    def test_when_parsing_character_given_titles_are_not_found_then_titles_are_not_scraped(self):
        """
        Tests that titles of the Fire Emblem character are not scraped when parsing the given response of the
        character's web page, given that titles of the character are not found in the given response.

        :return: None
        """
        html = '''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Ike</title>
                </head>
                <body>
                    <h1 id="firstHeading">Ike</h1>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertNotIn('titles', character_item, 'Titles were unexpectedly scraped')

    def test_when_parsing_character_given_only_english_voice_actors_are_found_then_only_english_voice_actors_are_scraped(
            self):
        """
        Tests that only English voice actors of the Fire Emblem character are scraped when parsing the given response of
        the character's web page, given that only English voice actors of the character are found in the given response.

        :return: None
        """
        voice_actors = {
            'english': ['David Lodge']
        }
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Jeralt</title>
                </head>
                <body>
                    <h1 id="firstHeading">Jeralt</h1>
                    <table>
                        <tr>
                            <th>Voiced by</th>
                            <td>
                                <ul>
                                    <li>
                                        <a href="https://en.wikipedia.org/wiki/David">{voice_actors['english'][0]}</a>
                                        <small>(English, Three Houses)</small>
                                    </li>
                                </ul>
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertEqual(character_item['voiceActors'], voice_actors, 'Voice actors were not scraped correctly')

    def test_when_parsing_character_given_only_japanese_voice_actors_are_found_then_only_japanese_voice_actors_are_scraped(
            self):
        """
        Tests that only Japanese voice actors of the Fire Emblem character are scraped when parsing the given response
        of the character's web page, given that only Japanese voice actors of the character are found in the given
        response.

        :return: None
        """
        voice_actors = {
            'japanese': ['Akio Ōtsuka']
        }
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Jeralt</title>
                </head>
                <body>
                    <h1 id="firstHeading">Jeralt</h1>
                    <table>
                        <tr>
                            <th>Voiced by</th>
                            <td>
                                <ul>
                                    <li>
                                        <a href="https://en.wikipedia.org/wiki/Akio">{voice_actors['japanese'][0]}</a>
                                        <small>(Japanese, Three Houses)</small>
                                    </li>
                                </ul>
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertEqual(character_item['voiceActors'], voice_actors, 'Voice actors were not scraped correctly')

    def test_when_parsing_character_given_english_and_japanese_voice_actors_are_found_then_english_and_japanese_voice_actors_are_scraped(
            self):
        """
        Tests that both English and Japanese voice actors of the Fire Emblem character are scraped when parsing the
        given response of the character's web page, given that both English and Japanese voice actors of the character
        are found in the given response.

        :return: None
        """
        voice_actors = {
            'english': ['David Lodge'],
            'japanese': ['Akio Ōtsuka']
        }
        html = f'''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Jeralt</title>
                </head>
                <body>
                    <h1 id="firstHeading">Jeralt</h1>
                    <table>
                        <tr>
                            <th>Voiced by</th>
                            <td>
                                <ul>
                                    <li>
                                        <a href="https://en.wikipedia.org/wiki/Akio">{voice_actors['japanese'][0]}</a>
                                        <small>(Japanese, Three Houses)</small>
                                    </li>
                                    <li>
                                        <a href="https://en.wikipedia.org/wiki/David">{voice_actors['english'][0]}</a>
                                        <small>(English, Three Houses)</small>
                                    </li>
                                </ul>
                            </td>
                        </tr>
                    </table>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertEqual(character_item['voiceActors'], voice_actors, 'Voice actors were not scraped correctly')

    def test_when_parsing_character_given_voice_actors_are_not_found_then_voice_actors_are_not_scraped(self):
        """
        Tests that voice actors are not scraped when parsing the given response of the character's web page, given that
        voice actors of the character are not found in the given response.

        :return: None
        """
        html = '''
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Jeralt</title>
                </head>
                <body>
                    <h1 id="firstHeading">Jeralt</h1>
                </body>
            </html>
        '''
        response = HtmlResponse(url='', body=html.encode('utf-8'))

        character_item = self.spider.parse_character(response)

        self.assertNotIn('voiceActors', character_item, 'Voice actors were unexpectedly scraped')

    if __name__ == '__main__':
        unittest.main()
