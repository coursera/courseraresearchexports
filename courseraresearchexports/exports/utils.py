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

from courseraresearchexports.exports.constants import COURSE_API, PARTNER_API
import logging
import os
import requests
import zipfile


def extract_export_archive(export_archive, dest, delete_archive=True):
    """
    Extracts a compressed folder
    :param export_archive:
    :param dest:
    :param delete_archive: delete the archive after extracting
    :return dest:
    """
    try:
        logging.debug('Extracting archive to {}'.format(dest))
        with zipfile.ZipFile(export_archive, 'r') as z:
            z.extractall(dest)
        if delete_archive:
            os.remove(export_archive)
        return dest
    except:
        logging.error('Error in extracting export archive {} to {}'.format(
            export_archive, dest))
        raise


def lookup_course_slug_by_id(course_id):
    """
    Find the course slug given an course_id
    """
    response = requests.get(requests.compat.urljoin(COURSE_API, course_id))
    response.raise_for_status()
    return response.json()['elements'][0]['slug']


def lookup_course_id_by_slug(course_slug):
    """
    Find the course_id given a course_slug
    """
    try:
        payload = {'q': 'slug', 'slug': course_slug}
        response = requests.get(COURSE_API, params=payload)
        response.raise_for_status()
        return response.json()['elements'][0]['id']

    except requests.exceptions.HTTPError:
        logging.error("""
            Could not retrieve course_id for {}.  Please check that the
            course slug was entered correctly.
            """.format(course_slug))
        raise


def lookup_partner_id_by_short_name(partner_short_name):
    """
    Find the partner_id by short name
    """
    try:
        payload = {'q': 'shortName', 'shortName': partner_short_name}
        response = requests.get(COURSE_API, params=payload)
        response.raise_for_status()
        return response.json()['elements'][0]['id']

    except requests.exceptions.HTTPError:
        logging.error(
            'Could not retrieve partner_id for {}. Please check that the '
            'partner short name was entered correctly.'
            .format(partner_short_name))
        raise


def lookup_partner_short_name_by_id(partner_id):
    """
    Find the partner_id by short name
    """
    response = requests.get(requests.compat.urljoin(PARTNER_API, partner_id))
    response.raise_for_status()
    return response.json()['elements'][0]['slug']
