import unittest
from unittest.mock import patch

from fire_emblem_data_scraper.pipelines.mongo_pipeline import MongoPipeline
from fire_emblem_data_scraper.utils.mock_item import MockItem
from fire_emblem_data_scraper.utils.mock_spider import MockSpider


class TestMongoPipeline(unittest.TestCase):
    """
    TestMongoPipeline is a class for unit testing MongoPipeline.
    """

    def setUp(self):
        """
        Method that executes before each test method.

        :return: None
        """
        self.spider = MockSpider()
        self.collection_name = 'collection'
        self.database_name = 'database'
        self.uri = '/uri'
        self.pipeline = MongoPipeline(self.collection_name, self.database_name, self.uri)

    @patch('fire_emblem_data_scraper.pipelines.mongo_pipeline.MongoClient')
    def test_when_opening_spider_then_mongo_connection_is_created(self, mongo_client_mock):
        """
        Tests that a connection to the MongoDB instance specified by the given URI is created when opening the given
        spider.

        :param mongo_client_mock: A mock of MongoClient
        :type mongo_client_mock: MagicMock
        :return: None
        """
        self.pipeline.open_spider(self.spider)

        mongo_client_mock.assert_called_once_with(self.uri)

    @patch('fire_emblem_data_scraper.pipelines.mongo_pipeline.MongoClient')
    def test_when_opening_spider_then_database_is_created_or_retrieved(self, mongo_client_mock):
        """
        Tests that the database specified by the given database name is created or retrieved when opening the given
        spider.

        :param mongo_client_mock: A mock of MongoClient
        :type mongo_client_mock: MagicMock
        :return: None
        """
        self.pipeline.open_spider(self.spider)

        self.assertEqual(self.pipeline.database, self.pipeline.client[self.database_name],
                         'Database was not created/retrieved')

    @patch('fire_emblem_data_scraper.pipelines.mongo_pipeline.MongoClient.close')
    def test_when_closing_spider_then_mongo_connection_is_closed(self, close_mock):
        """
        Tests that the connection to the MongoDB instance specified by the given URI is closed when closing the given
        spider.

        :param close_mock: A mock of the method for closing the MongoDB connection
        :type close_mock: MagicMock
        :return: None
        """
        self.pipeline.open_spider(self.spider)

        self.pipeline.close_spider(self.spider)

        close_mock.assert_called_once()

    @patch('pymongo.collection.Collection.insert_one')
    def test_when_processing_item_then_item_is_inserted_into_collection(self, insert_one_mock):
        """
        Tests that the given item is inserted into the collection specified by the given collection name when processing
        the item.

        :param insert_one_mock: A mock of the method for inserting a document into a MongoDB collection
        :type insert_one_mock: MagicMock
        :return: None
        """
        item = MockItem()
        self.pipeline.open_spider(self.spider)

        self.pipeline.process_item(item, self.spider)

        insert_one_mock.assert_called_once_with(dict(item))

    @patch('fire_emblem_data_scraper.pipelines.mongo_pipeline.MongoClient')
    def test_when_processing_item_then_item_is_returned(self, mongo_client_mock):
        """
        Tests that the given item is returned when processing the item.

        :param mongo_client_mock: A mock of MongoClient
        :type mongo_client_mock: MagicMock
        :return: None
        """
        item = MockItem()
        self.pipeline.open_spider(self.spider)

        result = self.pipeline.process_item(item, self.spider)

        self.assertIs(result, item, 'The given item was not returned')

    if __name__ == '__main__':
        unittest.main()
