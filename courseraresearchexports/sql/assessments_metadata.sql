/*
Bridge from course item to assessments.
Currently this query is quite slow (~4min for a medium size course).
Requires some investigation.
*/
WITH item_metadata AS
(
    SELECT course_item_id
        ,course_lesson_id
        ,course_module_id
        ,course_branch_id
        ,course_id
        ,course_branch_item_name
        ,course_branch_lesson_name
        ,course_branch_module_name
        ,authoring_course_branch_name
        ,course_item_type_desc
        ,assessment_id
        ,RANK() OVER(
            PARTITION BY course_branch_id, course_module_id
            ORDER BY course_branch_lesson_order, course_branch_item_order
        ) AS course_module_assessment_item_number
        ,SPLIT_PART(assessment_id, '@', 1) AS assessment_base_id
        ,SPLIT_PART(assessment_id, '@', 2)::INTEGER AS assessment_version
    FROM course_branch_items i
    JOIN course_branch_lessons
        USING(course_branch_id, course_lesson_id)
    JOIN course_branch_modules m
        USING(course_branch_id, course_module_id)
    JOIN course_branches
        USING(course_branch_id)
    JOIN course_branch_item_assessments
        USING(course_branch_id, course_item_id)
    JOIN course_item_types
        USING(course_item_type_id)
    WHERE course_item_type_category = 'quiz'
)

SELECT course_item_id
    ,course_lesson_id
    ,course_module_id
    ,course_branch_id
    ,course_id
    ,course_slug
    ,course_branch_item_name
    ,course_branch_lesson_name
    ,course_branch_module_name
    ,authoring_course_branch_name
    ,course_item_type_desc
    ,a.assessment_id
    ,assessment_type_id
    ,assessment_update_ts
    ,course_module_assessment_item_number
    ,i.assessment_id = a.assessment_id AS is_published_version
FROM item_metadata i
JOIN assessments a
    USING(assessment_base_id)
JOIN courses
    USING(course_id)
WHERE a.assessment_version <= i.assessment_version
;

