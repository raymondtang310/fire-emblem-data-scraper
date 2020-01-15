from unittest import mock, TestCase

from scrapy.http import HtmlResponse

from fire_emblem_data_scraper.spiders.characters.characters import CharactersSpider


class TestCharactersSpider(TestCase):
    """
    TestCharactersSpider is a class for unit testing CharactersSpider.
    """

    def setUp(self):
        """
        Instructions that execute before each test method.

        :return: None
        """
        self.spider = CharactersSpider()

    @mock.patch('fire_emblem_data_scraper.spiders.characters.characters.scrapy.Request')
    def test_request_is_made_for_each_character_link(self, mock_scrapy_request):
        """
        Tests that a request is made for each link to a Fire Emblem character web page that is found in the given
        response.

        :param mock_scrapy_request: A mock of scrapy.Request
        :type mock_scrapy_request: MagicMock
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
            mock_scrapy_request.assert_called_with(character_url, callback=self.spider.parse_character)

    @mock.patch('fire_emblem_data_scraper.spiders.characters.characters.scrapy.Request')
    def test_request_is_made_for_next_page_when_next_page_link_is_found(self, mock_scrapy_request):
        """
        Tests that a request is made for the next page when a link for the next page is found in the given response.

        :param mock_scrapy_request: A mock of scrapy.Request
        :type mock_scrapy_request: MagicMock
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
            mock_scrapy_request.assert_called_with(next_page_url, callback=self.spider.parse)

    @mock.patch('fire_emblem_data_scraper.spiders.characters.characters.scrapy.Request')
    def test_request_is_not_made_for_next_page_when_next_page_link_is_not_found(self, mock_scrapy_request):
        """
        Tests that a request is not made for the next page when a link for the next page is not found in the given
        response.

        :param mock_scrapy_request: A mock of scrapy.Request
        :type mock_scrapy_request: MagicMock
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
            mock_scrapy_request.assert_not_called()

    def test_parse_name_when_name_is_found(self):
        """
        Tests that the name of the Fire Emblem character is parsed correctly when the name of the character is found in
        the given response.

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

        self.assertEqual(character_item['name'], name, 'Name was not parsed correctly')

    def test_parse_name_when_name_is_not_found(self):
        """
        Tests that a CharacterItem is not returned when the name of the Fire Emblem character cannot be found in the
        given response.

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

        self.assertIsNone(result, 'None should have been returned')

    def test_parse_images_when_primary_displayed_image_is_found(self):
        """
        Tests that images are parsed correctly when a primary displayed image is found in the given response.

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

        self.assertEqual(character_item['primaryImage'], primary_image_url, 'Primary image was not parsed correctly')
        self.assertEqual(character_item['otherImages'], other_images_urls, 'Other images were not parsed correctly')

    def test_parse_images_when_primary_displayed_image_is_not_found_and_other_images_are_found(self):
        """
        Tests that images are parsed correctly when a primary displayed image cannot be found in the given response
        but other images are found.

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

        self.assertEqual(character_item['primaryImage'], primary_image_url, 'Primary image was not parsed correctly')
        self.assertEqual(character_item['otherImages'], other_images_urls, 'Other images were not parsed correctly')

    def test_parse_images_when_no_images_are_found(self):
        """
        Tests that images are not added to the parsed CharacterItem when no images of the Fire Emblem character
        are found in the given response.

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

        self.assertNotIn('primaryImage', character_item, 'CharacterItem should not contain a primary image')
        self.assertNotIn('otherImages', character_item, 'CharacterItem should not contain other images')

    def test_parse_appearances_when_appearances_are_found(self):
        """
        Tests that the appearances of the Fire Emblem character are parsed correctly when the character's appearances
        are found in the given response.

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

        self.assertEqual(character_item['appearances'], appearances, 'Appearances were not parsed correctly')

    def test_parse_appearances_when_no_appearances_are_found(self):
        """
        Tests that appearances are not added to the parsed CharacterItem when the character's appearances cannot be
        found in the given response.

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

        self.assertNotIn('appearances', character_item, 'CharacterItem should not contain appearances')

    def test_parse_titles_when_multiple_titles_are_found(self):
        """
        Tests that the titles of the Fire Emblem character are parsed correctly when multiple titles for the character
        are found in the given response.

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

        self.assertEqual(character_item['titles'], titles, 'Titles were not parsed correctly')

    def test_parse_titles_when_title_text_is_split_amongst_multiple_elements(self):
        """
        Tests that the titles of the Fire Emblem character are parsed correctly when the text of a title for the
        character is split amongst multiple elements in the given response.

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

        self.assertEqual(character_item['titles'], titles, 'Titles were not parsed correctly')

    def test_parse_titles_when_one_title_is_found(self):
        """
        Tests that the titles of the Fire Emblem character are parsed correctly when only one title for the character
        is found in the given response.

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

        self.assertEqual(character_item['titles'], titles, 'Titles were not parsed correctly')

    def test_parse_titles_when_no_titles_are_found(self):
        """
        Tests that titles are not added to the parsed CharacterItem when titles for the character cannot be found in the
        given response.

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

        self.assertNotIn('titles', character_item, 'CharacterItem should not contain titles')

    def test_parse_voice_actors_when_only_english_voice_actors_are_found(self):
        """
        Tests that the voice actors of the Fire Emblem character are parsed correctly when only the character's English
        voice actors are found in the given response.

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

        self.assertEqual(character_item['voiceActors'], voice_actors, 'Voice actors were not parsed correctly')

    def test_parse_voice_actors_when_only_japanese_voice_actors_are_found(self):
        """
        Tests that the voice actors of the Fire Emblem character are parsed correctly when only the character's Japanese
        voice actors are found in the given response.

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

        self.assertEqual(character_item['voiceActors'], voice_actors, 'Voice actors were not parsed correctly')

    def test_parse_voice_actors_when_english_and_japanese_voice_actors_are_found(self):
        """
        Tests that the voice actors of the Fire Emblem character are parsed correctly when both the character's English
        and Japanese voice actors are found in the given response.

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

        self.assertEqual(character_item['voiceActors'], voice_actors, 'Voice actors were not parsed correctly')

    def test_parse_voice_actors_when_no_voice_actors_are_found(self):
        """
        Tests that voice actors are not added to the parsed CharacterItem when no voice actors are found in the given
        response.

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

        self.assertNotIn('voiceActors', character_item, 'CharacterItem should not contain voice actors')
