# Copyright 2016 Coursera
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Coursera's wrapper for data exports API.
"""

import requests
from courseraoauth2client import oauth2
from courseraresearchexports.models.utils import requests_response_to_model
from courseraresearchexports.constants.api_constants import \
    RESEARCH_EXPORTS_APP, RESEARCH_EXPORTS_API, CLICKSTREAM_API
from courseraresearchexports.models.ExportRequestWithMetadata import \
    ExportRequestWithMetadata


@requests_response_to_model(ExportRequestWithMetadata.from_response)
def get(export_job_id):
    """
    Use Coursera's Research Export Resource to get a data export job given an
    export job id.
    :param export_job_id:
    :return export_request_with_metadata: [ExportRequestWithMetaData]
    """
    auth = oauth2.build_oauth2(app=RESEARCH_EXPORTS_APP).build_authorizer()
    response = requests.get(
        url=requests.compat.urljoin(RESEARCH_EXPORTS_API, export_job_id),
        auth=auth)

    return response


@requests_response_to_model(ExportRequestWithMetadata.from_response)
def get_all():
    """
    Uses Coursera's Research Exports Resource to get all data export job
    requests created by a user. Limited to the 100 most recent requests.
    :return export_requests: [ExportRequestWithMetaData]
    """
    auth = oauth2.build_oauth2(app=RESEARCH_EXPORTS_APP).build_authorizer()
    response = requests.get(
        url=RESEARCH_EXPORTS_API,
        auth=auth,
        params={'q': 'my'})

    return response


@requests_response_to_model(ExportRequestWithMetadata.from_response)
def post(export_request):
    """
    Creates a data export job using a formatted json request.
    :param export_request:
    :return export_request_with_metadata: [ExportRequestWithMetadata]
    """
    auth = oauth2.build_oauth2(app=RESEARCH_EXPORTS_APP).build_authorizer()
    response = requests.post(
        url=RESEARCH_EXPORTS_API,
        json=export_request.to_json(),
        auth=auth)

    return response


@requests_response_to_model(lambda response: response.json())
def get_clickstream_download_links(clickstream_download_links_request):
    """
    Return the download links for clickstream exports in a given scope.
    :param clickstream_download_links_request: ClickstreamDownloadLinksRequest
    """
    auth = oauth2.build_oauth2(app=RESEARCH_EXPORTS_APP).build_authorizer()
    response = requests.post(
        url=CLICKSTREAM_API,
        params=clickstream_download_links_request.to_url_params(),
        auth=auth)

    return response
