class MinerException(Exception):
    """ base exception class for the miner package """

class SymbolError(MinerException):
    """ symbol is not recognizable """

class GetError(MinerException):
    """ failed to get the content requested """

class ScrapingError(MinerException):
    """ failed to extract values out from the html content """

class PreprocessingError(MinerException):
    """ failed to preprocess raw data """
