import scrapy


class CharacterItem(scrapy.Item):
    """
    CharacterItem encapsulates data on a Fire Emblem character.
    """
    name = scrapy.Field()
    primaryImage = scrapy.Field()
    otherImages = scrapy.Field()
    titles = scrapy.Field()
    appearances = scrapy.Field()
    voiceActors = scrapy.Field()
