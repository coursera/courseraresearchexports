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

import json
import requests
from courseraoauth2client import oauth2

from courseraresearchexports.exports.constants import RESEARCH_EXPORTS_APP, \
    RESEARCH_EXPORTS_API


def get(export_job_id):
    """
    Uses Coursera API to get an export job given an export job id
    :param export_job_id:
    :return export_job:
    """
    auth = oauth2.build_oauth2(app=RESEARCH_EXPORTS_APP).build_authorizer()
    response = requests.get(
        url=requests.compat.urljoin(RESEARCH_EXPORTS_API, export_job_id),
        auth=auth)
    response.raise_for_status()
    export_job = response.json()['elements'][0]

    return export_job


def get_all():
    """
    Uses Coursera's export API to get all export jobs created by a user.
     Coursera's export job resource limits this to the 100 most recent jobs.
    :return export_jobs:
    """
    auth = oauth2.build_oauth2(app=RESEARCH_EXPORTS_APP).build_authorizer()
    response = requests.get(
        url=RESEARCH_EXPORTS_API,
        auth=auth,
        params={'q': 'my'})
    response.raise_for_status()
    export_jobs = json.loads(json.dumps(response.json()))['elements']

    return export_jobs


def create(export_job_json):
    """
    Creates a Coursera research export job using a formatted json request.
    :param export_job_json:
    :return export_job_id:
    """
    auth = oauth2.build_oauth2(app=RESEARCH_EXPORTS_APP).build_authorizer()
    response = requests.post(
        url=RESEARCH_EXPORTS_API,
        json=export_job_json,
        auth=auth)
    response.raise_for_status()
    export_job_id = response.json()['elements'][0]['id']

    return export_job_id
