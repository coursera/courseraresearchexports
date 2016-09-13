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

import logging

import requests

from courseraresearchexports.constants.api_constants import \
    COURSE_API, PARTNER_API


def requests_response_to_model(response_transformer):
    """
    Creates decorator to handles errors in response from API call and
    transforms response with response_handler_func
    :param response_transformer: function(response) -> Any
    :return:
    """
    def response_transform_decorator(original_func):
        """
        Creates wrapper around a function that returns response
        """
        def response_transformer_wrapper(*args, **kwargs):
            """
            Log errors and apply transformation in response_handler_func
            """
            try:
                response = original_func(*args, **kwargs)
                response.raise_for_status()

            except requests.exceptions.HTTPError:
                logging.error(
                    'Request to {url} with body:\n\t{body}\nreceived response'
                    ':\n\t{text}\nPlease check request or contact '
                    'data-support@coursera.org if this error persists.'
                    .format(url=response.url,
                            text=response.text,
                            body=(response.request and response.request.body)))
                raise

            return response_transformer(response)
        return response_transformer_wrapper
    return response_transform_decorator


@requests_response_to_model(
    lambda response: response.json()['elements'][0]['slug'])
def lookup_course_slug_by_id(course_id):
    """
    Find the course slug given an course_id
    """
    return requests.get(requests.compat.urljoin(COURSE_API, course_id))


@requests_response_to_model(
    lambda response: response.json()['elements'][0]['id'])
def lookup_course_id_by_slug(course_slug):
    """
    Find the course_id given a course_slug
    """
    payload = {'q': 'slug', 'slug': course_slug}
    return requests.get(COURSE_API, params=payload)


@requests_response_to_model(
    lambda response: response.json()['elements'][0]['id'])
def lookup_partner_id_by_short_name(partner_short_name):
    """
    Find the partner_id by short name
    """
    payload = {'q': 'shortName', 'shortName': partner_short_name}
    return requests.get(COURSE_API, params=payload)


@requests_response_to_model(
    lambda response: response.json()['elements'][0]['shortName'])
def lookup_partner_short_name_by_id(partner_id):
    """
    Find the partner_id by short name
    """
    return requests.get(requests.compat.urljoin(PARTNER_API, str(partner_id)))
