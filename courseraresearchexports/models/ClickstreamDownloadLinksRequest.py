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

from courseraresearchexports.models import utils


class ClickstreamDownloadLinksRequest:
    """
    Represents a request for clickstream download links.
    """

    def __init__(self, course_id=None, partner_id=None, interval=None,
                 **kwargs):
        self.course_id = course_id
        self.partner_id = partner_id
        self.interval = interval

    @staticmethod
    def from_args(**kwargs):
        """
        Create a ClickstreamDownloadLinkRequest from arguments. Performs
        course_id/partner_id inference.
        :param kwargs:
        :return eventing_links_request: ClickstreamDownloadLinksRequest
        """
        if kwargs.get('course_slug') and not kwargs.get('course_id'):
            kwargs['course_id'] = utils.lookup_course_id_by_slug(
                kwargs['course_slug'])
        elif kwargs.get('partner_short_name') and not kwargs.get('partner_id'):
            kwargs['partner_id'] = \
                utils.lookup_partner_id_by_short_name(
                    kwargs['partner_short_name'])
        elif kwargs.get('group_id'):
            logging.error(
                'Eventing exports by group is not currently supported. '
                'Please see https://coursera.gitbooks.io/data-exports/content/'
                'introduction/programmatic_access.html')
            raise ValueError('Eventing exports by group is not supported.')

        return ClickstreamDownloadLinksRequest(**kwargs)

    @property
    def scope(self):
        """
        API specific format for request scope context.
        :return scope:
        """
        if self.course_id:
            return 'courseContext~{}'.format(self.course_id)
        elif self.partner_id:
            return 'partnerContext~{}'.format(self.partner_id)

    def to_url_params(self):
        """
        API specific parameters for POST request.
        :return:
        """
        url_params = {'action': 'generateLinks', 'scope': self.scope}
        if self.interval:
            url_params['startDate'] = self.interval[0]
            url_params['endDate'] = self.interval[1]

        return url_params
