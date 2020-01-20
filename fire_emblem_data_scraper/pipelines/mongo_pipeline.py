import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class MongoPipeline(object):
    """
    MongoPipeline stores items scraped by spiders as documents into a MongoDB collection.
    """

    def __init__(self, collection_name, database_name, uri):
        """
        Initializes the MongoPipeline with the given MongoDB URI, name of the database, and name of the collection under
        which items scraped by spiders will be stored as documents.

        :param collection_name: The name of the collection under which documents will be stored
        :type collection_name: string
        :param database_name: The name of the database that contains or will contain the collection specified by
        collection_name
        :type database_name: string
        :param uri: The URI of the MongoDB instance that contains or will contain the database specified by
        db_name
        :type uri: string

        :return None
        """
        self.collection_name = collection_name
        self.database_name = database_name
        self.uri = uri

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            collection_name=crawler.settings.get('MONGO_COLLECTION_NAME'),
            database_name=crawler.settings.get('MONGO_DATABASE_NAME', 'fireEmblemData'),
            uri=crawler.settings.get('MONGO_URI', os.getenv('MONGO_URI'))
        )

    def open_spider(self, spider):
        self.client = MongoClient(self.uri)
        self.database = self.client[self.database_name]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.database[self.collection_name].insert_one(dict(item))
        return item
