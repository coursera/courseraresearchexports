#!/usr/bin/env python

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

from courseraoauth2client import oauth2
from courseraresearchexports.exports.constants import RESEARCH_EXPORTS_APP, \
    RESEARCH_EXPORTS_API, EVENTING_API
from courseraresearchexports.models.ExportRequest import \
    ExportRequestWithMetadata
import requests


def get(export_job_id):
    """
    Use Coursera's Research Export Resource to get a data export job given an
    export job id.
    :param export_job_id:
    :return export_request: ExportRequestWithMetaData
    """
    auth = oauth2.build_oauth2(app=RESEARCH_EXPORTS_APP).build_authorizer()
    response = requests.get(
        url=requests.compat.urljoin(RESEARCH_EXPORTS_API, export_job_id),
        auth=auth)
    response.raise_for_status()

    return ExportRequestWithMetadata.from_json(response.json()['elements'][0])


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
    response.raise_for_status()
    export_requests = [ExportRequestWithMetadata.from_json(export_request)
                       for export_request in response.json()['elements']]

    return export_requests


def post(export_request):
    """
    Creates a data export job using a formatted json request.
    :param export_request:
    :return export_request_with_metadata: ExportRequestWithMetadata
    """
    auth = oauth2.build_oauth2(app=RESEARCH_EXPORTS_APP).build_authorizer()
    response = requests.post(
        url=RESEARCH_EXPORTS_API,
        json=export_request.to_json(),
        auth=auth)
    response.raise_for_status()

    return ExportRequestWithMetadata.from_json(response.json()['elements'][0])


def get_eventing_download_links(eventing_links_request):
    """
    Return the download links for eventing exports in a given scope.
    :param eventing_links_request: EventingDownloadLinksRequest
    """
    auth = oauth2.build_oauth2(app=RESEARCH_EXPORTS_APP).build_authorizer()
    response = requests.post(
        url=EVENTING_API,
        params=eventing_links_request.to_url_params(),
        auth=auth)

    return response.json()
