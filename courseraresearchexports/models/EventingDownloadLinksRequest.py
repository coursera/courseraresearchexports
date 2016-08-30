import logging

from courseraresearchexports.exports import utils


class EventingDownloadLinksRequest:
    """
    Represents an eventing downloading links request.
    """

    def __init__(self, course_id=None, partner_id=None, interval=None,
                 **kwargs):
        self.course_id = course_id
        self.partner_id = partner_id
        self.interval = interval

    @staticmethod
    def from_args(**kwargs):
        """
        Create a EventingDownloadLinkRequest from arguments. Performs
        course_id/partner_id inference.
        :param kwargs:
        :return eventing_links_request: EventingDownloadLinksRequest
        """
        if kwargs.get('course_slug') and not kwargs.get('course_id'):
            kwargs['course_id'] = utils.lookup_course_id_by_slug(
                kwargs['course_slug'])
        elif kwargs.get('partner_short_name') and not kwargs.get('partner_id'):
            kwargs['partner_id'] = utils.lookup_partner_id_by_short_name(
                kwargs['partner_short_name'])
        elif kwargs.get('group_id'):
            logging.error("""
                Eventing exports by group is not currently supported.
                Please see https://coursera.gitbooks.io/data-exports/content/
                introduction/programmatic_access.html""")
            raise ValueError('Eventing exports by group is not supported.')

        return EventingDownloadLinksRequest(**kwargs)

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
