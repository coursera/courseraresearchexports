RESEARCH_EXPORTS_APP = 'manage_research_exports'
RESEARCH_EXPORTS_API = 'https://www.coursera.org/api/onDemandExports.v2/'
COURSE_API = 'https://www.coursera.org/api/onDemandCourses.v1/'
PARTNER_API = 'https://www.coursera.org/api/partners.v1/'
EVENTING_API = 'https://www.coursera.org/api/clickstreamExportsDownload.v1/'

ANONYMITY_LEVEL_COORDINATOR = 'HASHED_IDS_NO_PII'
ANONYMITY_LEVEL_ISOLATED = 'HASHED_IDS_WITH_ISOLATED_UGC_NO_PII'
ANONYMITY_LEVELS = [ANONYMITY_LEVEL_COORDINATOR, ANONYMITY_LEVEL_ISOLATED]

EXPORT_TYPE_SCHEMAS = 'RESEARCH_WITH_SCHEMAS'
EXPORT_TYPE_EVENTING = 'RESEARCH_EVENTING'
EXPORT_TYPE_GRADEBOOK = 'GRADEBOOK'
EXPORT_TYPES = [EXPORT_TYPE_SCHEMAS, EXPORT_TYPE_EVENTING,
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
