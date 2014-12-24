class MinerException(Exception):
    """ base exception class for the miner package """

class SymbolError(MinerException):
    """ symbol is not recognizable """

class GetError(MinerException):
    """ failed to get the content requested """
