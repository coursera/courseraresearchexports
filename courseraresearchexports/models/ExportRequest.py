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

from courseraresearchexports.constants.api_constants import \
    ANONYMITY_LEVEL_COORDINATOR, ANONYMITY_LEVEL_ISOLATED, EXPORT_TYPE_TABLES,\
    EXPORT_TYPE_CLICKSTREAM, EXPORT_TYPE_GRADEBOOK, SCHEMA_NAMES
from courseraresearchexports.models import utils


class ExportRequest:
    """
    Represents a export request for Coursera's research data export
    service and provides methods for serialization.
    """

    def __init__(self, course_id=None, partner_id=None, group_id=None,
                 export_type=None, anonymity_level=None,
                 statement_of_purpose=None, schema_names=None,
                 interval=None, ignore_existing=None, **kwargs):
        self._course_id = course_id
        self._partner_id = partner_id
        self._group_id = group_id
        self._export_type = export_type
        self._anonymity_level = anonymity_level
        self._statement_of_purpose = statement_of_purpose
        self._schema_names = schema_names
        self._interval = interval
        self._ignore_existing = ignore_existing

    def to_json(self):
        """
        Serialize ExportRequest to a dictionary representing a json object.
        No validation is done with the exception that only specification of
        scope is used (course/partner/group).
        :return json_request:
        """
        json_request = {}

        if self._course_id:
            json_request['scope'] = {
                'typeName': 'courseContext',
                'definition': {
                    'courseId': self._course_id
                }}
        elif self._partner_id:
            json_request['scope'] = {
                'typeName': 'partnerContext',
                'definition': {
                    'partnerId': {
                        'maestroId': self._partner_id
                    }}}
        elif self._group_id:
            json_request['scope'] = {
                'typeName': 'groupContext',
                'definition': {
                    'groupId': self._group_id
                }}
        if self._export_type:
            json_request['exportType'] = self._export_type
        if self._anonymity_level:
            json_request['anonymityLevel'] = self._anonymity_level
        if self._statement_of_purpose:
            json_request['statementOfPurpose'] = self._statement_of_purpose
        if self._schema_names:
            json_request['schemaNames'] = self._schema_names
        if self._interval:
            json_request['interval'] = {
                'start': self._interval[0], 'end': self._interval[1]}
        if self._ignore_existing:
            json_request['ignoreExisting'] = self._ignore_existing

        return json_request

    @classmethod
    def from_args(cls, **kwargs):
        """
        Create a ExportResource object using the parameters required. Performs
        course_id/partner_id inference if possible.
        :param kwargs:
        :return export_request: ExportRequest
        """
        if kwargs.get('course_slug') and not kwargs.get('course_id'):
            kwargs['course_id'] = utils.lookup_course_id_by_slug(
                kwargs['course_slug'])
        elif kwargs.get('partner_short_name') and not kwargs.get('partner_id'):
            kwargs['partner_id'] = utils.lookup_partner_id_by_short_name(
                kwargs['partner_short_name'])

        if kwargs.get('user_id_hashing'):
            if kwargs['user_id_hashing'] == 'linked':
                kwargs['anonymity_level'] = ANONYMITY_LEVEL_COORDINATOR
            elif kwargs['user_id_hashing'] == 'isolated':
                kwargs['anonymity_level'] = ANONYMITY_LEVEL_ISOLATED

        return cls(**kwargs)

    @classmethod
    def from_json(cls, json_request):
        """
        Deserialize ExportRequest from json object.
        :param json_request:
        :return export_request: ExportRequest
        """
        kwargs = {}
        request_scope = json_request['scope']
        request_scope_context = request_scope['typeName']

        if request_scope_context == 'courseContext':
            kwargs['course_id'] = request_scope['definition']['courseId']
        elif request_scope_context == 'partnerContext':
            kwargs['partner_id'] = \
                request_scope['definition']['partnerId']['maestroId']
        elif request_scope_context == 'groupContext':
            kwargs['group_id'] = request_scope['definition']['groupId']

        if json_request.get('interval'):
            kwargs['interval'] = [
                json_request['interval']['start'],
                json_request['interval']['end']
            ]

        return cls(
            export_type=json_request.get('exportType'),
            anonymity_level=json_request.get('anonymityLevel'),
            statement_of_purpose=json_request.get('statementOfPurpose'),
            schema_names=json_request.get('schemaNames'),
            ignore_existing=json_request.get('ignoreExisting'),
            **kwargs)

    @property
    def course_id(self):
        return self._course_id

    @property
    def partner_id(self):
        return self._partner_id

    @property
    def export_type(self):
        return self._export_type

    @property
    def export_type_display(self):
        if self._export_type == EXPORT_TYPE_GRADEBOOK:
            return 'GRADEBOOK'
        elif self._export_type == EXPORT_TYPE_CLICKSTREAM:
            return 'CLICKSTREAM'
        elif self._export_type == EXPORT_TYPE_TABLES:
            return 'TABLES'
        else:
            return self._export_type

    @property
    def anonymity_level(self):
        return self._anonymity_level

    @property
    def formatted_anonymity_level(self):
        if self.anonymity_level == ANONYMITY_LEVEL_COORDINATOR:
            return 'Linked'
        elif self.anonymity_level == ANONYMITY_LEVEL_ISOLATED:
            return 'Isolated'
        else:
            return 'Unknown'

    @property
    def statement_of_purpose(self):
        return self._statement_of_purpose

    @property
    def interval(self):
        return self._interval

    @property
    def ignore_existing(self):
        return self._ignore_existing

    @property
    def scope_context(self):
        """
        Context for this ExportRequest, assume that only one identifier for
        partner/course/group is defined.
        """
        if self._course_id:
            return 'COURSE'
        elif self._partner_id:
            return 'PARTNER'
        elif self._group_id:
            return 'GROUP'
        else:
            return None

    @property
    def scope_id(self):
        """
        Identifier for the scope, assume that only one of course/partner/group
        is defined for a valid request.
        :return scope_id:
        """
        return self._course_id or self._partner_id or self._group_id

    @property
    def scope_name(self):
        """
        Human readable name for this scope context. course slugs for courses,
        partner short names for partners, but only group ids for groups (api is
        not open)
        :return:
        """
        if self._course_id:
            return utils.lookup_course_slug_by_id(self._course_id)
        elif self._partner_id:
            return utils.lookup_partner_short_name_by_id(self._partner_id)
        elif self._group_id:
            return self._group_id
        else:
            return 'UNKNOWN'

    @property
    def schema_names(self):
        return self._schema_names

    @property
    def schema_names_display(self):
        """
        Display only property for schemas names.
        :return schemas:
        """
        if self._schema_names:
            if set(self._schema_names) == set(SCHEMA_NAMES):
                return 'all'
            else:
                return ','.join(self._schema_names)
        else:
            return None

    def __eq__(self, other):
        """
        Override for internal equality checks as suggested at:
        http://stackoverflow.com/a/390640
        """
        if type(other) is type(self):
            return self.__dict__ == other.__dict__
        return False
