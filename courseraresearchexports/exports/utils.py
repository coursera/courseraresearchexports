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
import os
from urlparse import urlparse

from tqdm import tqdm
import requests

from courseraresearchexports.constants.api_constants import \
    EXPORT_TYPE_CLICKSTREAM, EXPORT_TYPE_TABLES

from courseraresearchexports.exports import api
from courseraresearchexports.models.ClickstreamDownloadLinksRequest import \
    ClickstreamDownloadLinksRequest


def download(export_request, dest):
    """
    Download a data export job using a request id.
    """
    try:
        is_table_export = export_request.export_type == EXPORT_TYPE_TABLES
        is_clickstream_export = \
            export_request.export_type == EXPORT_TYPE_CLICKSTREAM

        if not export_request.download_link:
            if export_request.status in ['PENDING', 'IN_PROGRESS']:
                logging.error(
                    'Export request {} is currently {} and is not ready for'
                    'download. Please wait until the request is completed.'
                    .format(export_request.id, export_request.status))
                raise ValueError(
                    'Export request is not yet ready for download')
            elif export_request.status == 'TERMINATED':
                logging.error(
                    'Export request has been TERMINATED. Please contact '
                    'data-support@coursera.org if we have not resolved this '
                    'within 24 hours.')
                raise ValueError('Export request has been TERMINATED')
            elif is_clickstream_export:
                # We don't fill in download links for clickstream exports
                pass
            else:
                logging.error('Download link was not found.')
                raise ValueError('Download link was not found')

        if not os.path.exists(dest):
            logging.info('Creating destination folder: {}'.format(dest))
            os.makedirs(dest)

        if is_table_export:
            return [download_url(export_request.download_link, dest)]
        elif is_clickstream_export:
            links_request = ClickstreamDownloadLinksRequest.from_args(
                course_id=export_request.course_id,
                partner_id=export_request.partner_id,
                interval=export_request.interval)
            download_links = api.get_clickstream_download_links(links_request)
            return [download_url(link, dest) for link in download_links]
        else:
            raise ValueError('Require export_type is one of {} or {}'.format(
                EXPORT_TYPE_TABLES,
                EXPORT_TYPE_CLICKSTREAM))

    except Exception as err:
        logging.error('Download failed.\n{err}'.format(err=err))
        raise


def download_url(url, dest_folder):
    """
    Download url to dest_folder/FILENAME, where FILENAME is the last
    part of the url path.
    """
    filename = urlparse(url).path.split('/')[-1]
    full_filename = os.path.join(dest_folder, filename)
    response = requests.get(url, stream=True)
    chunk_size = 1024 * 1024
    logging.debug('Writing to file: {}'.format(full_filename))

    with open(full_filename, 'wb') as f:
        for data in tqdm(
                iterable=response.iter_content(chunk_size),
                total=int(response.headers['Content-length']) / chunk_size,
                unit='MB',
                desc=filename):
            f.write(data)
    return full_filename
