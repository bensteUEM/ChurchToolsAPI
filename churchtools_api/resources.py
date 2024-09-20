import json
import logging
from datetime import datetime, timedelta

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract


class ChurchToolsApiResources(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on resources.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self):
        super()

    def get_resource_masterdata(self, result_type: str) -> dict:
        """Access to resource masterdata

        Arguments:
            result_type: either "resourceTypes" or "resources" depending on expected result

        Returns:
            dict of resource masterdata
        """
        known_result_types = ["resourceTypes", "resources"]
        if result_type not in known_result_types:
            logging.error(
                "get_resource_masterdata does not know result_type=%s", result_type
            )
            return

        url = self.domain + "/api/resource/masterdata"
        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)

            response_data = self.combine_paginated_response_data(
                response_content, url=url, headers=headers
            )

            return response_data[result_type]
        else:
            logging.error(response)
            return