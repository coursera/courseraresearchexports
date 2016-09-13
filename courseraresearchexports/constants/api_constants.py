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


RESEARCH_EXPORTS_APP = 'manage_research_exports'
RESEARCH_EXPORTS_API = 'https://www.coursera.org/api/onDemandExports.v2/'
COURSE_API = 'https://www.coursera.org/api/onDemandCourses.v1/'
PARTNER_API = 'https://www.coursera.org/api/partners.v1/'
CLICKSTREAM_API = 'https://www.coursera.org/api/clickstreamExportsDownload.v1/'
ANONYMITY_LEVEL_COORDINATOR = 'HASHED_IDS_NO_PII'
ANONYMITY_LEVEL_ISOLATED = 'HASHED_IDS_WITH_ISOLATED_UGC_NO_PII'
ANONYMITY_LEVELS = [ANONYMITY_LEVEL_COORDINATOR, ANONYMITY_LEVEL_ISOLATED]
EXPORT_TYPE_TABLES = 'RESEARCH_WITH_SCHEMAS'
EXPORT_TYPE_CLICKSTREAM = 'RESEARCH_EVENTING'
EXPORT_TYPE_GRADEBOOK = 'GRADEBOOK'
EXPORT_TYPES = [EXPORT_TYPE_TABLES, EXPORT_TYPE_CLICKSTREAM,
                EXPORT_TYPE_GRADEBOOK]
SCHEMA_NAMES = [
    'demographics',
    'users',
    'course_membership',
    'course_progress',
    'feedback',
    'assessments',
    'course_grades',
    'peer_assignments',
    'discussions',
    'programming_assignments',
    'course_content']
