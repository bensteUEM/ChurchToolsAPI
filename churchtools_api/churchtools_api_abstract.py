from abc import ABC, abstractmethod
import json
import logging

logger = logging.getLogger(__name__)

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
                for page in range(pagination["current"], pagination["lastPage"]):
                    logger.debug(
                        "running paginated request for page {} of {}".format(
                            page + 1,
                            pagination["lastPage"],
                        )
                    )
                    new_param = {"page": page + 1}
                    if kwargs.get("params"):
                        kwargs["params"].update(new_param)
                    else:
                        kwargs["params"] = new_param

                    response = self.session.get(url=url, **kwargs)
                    response_content = json.loads(response.content)
                    response_data.extend(response_content["data"])
        return response_data
