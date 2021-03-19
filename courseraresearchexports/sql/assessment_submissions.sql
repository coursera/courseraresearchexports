/*
Returns 1 row per assessment submission that is bridged to the course item
corresponding to that particular assessment.
*/
WITH action_ids_with_responses AS
(
    SELECT DISTINCT course_branch_id
        ,course_item_id
        ,assessment_action_id
    FROM assessment_responses
    JOIN course_branch_item_assessments
        USING(assessment_id)
)

SELECT course_id
	,course_branch_id
    ,course_item_id
    ,assessment_id
    ,assessment_action_id
    ,[assessments_user_id]
    ,assessment_action_ts
    ,assessment_action_ts = MIN(assessment_action_ts) OVER(
        PARTITION BY assessment_id, [assessments_user_id]
    ) AS is_first_submission
    ,assessment_action_ts = MAX(assessment_action_ts) OVER(
        PARTITION BY assessment_id, [assessments_user_id]
    ) AS is_last_submission
    ,assessment_action_ts = MIN(assessment_action_ts) OVER(
        PARTITION BY course_id, course_item_id, [assessments_user_id]
    ) AS is_first_item_submission
FROM assessment_actions
JOIN action_ids_with_responses
    USING(assessment_action_id)
JOIN course_branches
	USING(course_branch_id)
;
