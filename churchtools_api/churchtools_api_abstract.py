from abc import ABC, abstractmethod


class ChurchToolsApiAbstract(ABC):
    """This abstract is used to define minimum references available for all api parts

    Args:
        ABC: python default abstract
    """
    @abstractmethod
    def __init__(self):
        self.session = None
        self.domain = None
