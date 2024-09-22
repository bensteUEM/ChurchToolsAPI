from abc import ABC, abstractmethod
import logging

class ChurchToolsApiAbstract(ABC):
    """This abstract is used to define minimum references available for all api parts

    Args:
        ABC: python default abstract
    """
    @abstractmethod
    def __init__(self):
        self.session = None
        self.domain = None

    def combine_paginated_response_data(
        self, response_content: dict, url: str, **kwargs
    ) -> dict:
        """Helper function which combines data for requests in case of paginated responses

        Args:
            response_content: the original response form ChurchTools which either has meta/pagination or not
            url: the url used for the original request in order to repear it
            kwargs - can contain headers and params passthrough

        Returns:
            response 'data' without pagination
        """
        response_data = response_content["data"].copy()

        if meta := response_content.get("meta"):
            if pagination := meta.get("pagination"):
                while pagination["current"] < pagination["lastPage"]:
                    logging.debug(
                        "page {} of {}".format(
                            pagination["current"],
                            pagination["lastPage"],
                        )
                    )
                    params = {"page": pagination["current"] + 1}
                    response = self.session.get(url=url, **kwargs)
                    response_content = json.loads(response.content)
                    response_data.extend(response_content["data"])
        return response_data
