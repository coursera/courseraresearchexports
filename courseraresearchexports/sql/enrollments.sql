/*
enrollments
An enrollment is a unique learner-course pair. Many tables log a learner's
interactions in a course, and this view will aggregate key metrics for simple
reporting purposes.

Columns
coursera_user_id
course_id
commenced_dt
is_enrollment_active
activity_first_dt
activity_last_dt    
num_days_active
is_enrollment_completed
completion_dt
was_paid_or_finaid
*/

/*
Any user that reaches the LEARNER membership role in a course is considered a
commenced enrolllment. This excludes those users that pre-enroll in the course,
and then later unenrolls before the course starts.
*/
WITH enrollment_commenced AS (
    SELECT
        cm.[partner_user_id]
        ,course_id
        ,MIN(course_membership_ts)::DATE AS commenced_dt
    FROM course_memberships AS cm
    WHERE
        course_membership_role = 'LEARNER'
    GROUP BY 1,2    
)    

/*
Learners' progress on course items (e.g. lectures, quizzes, etc.) are
summarized in the course_progress table. Generate their "activity" metrics with
aggregate functions.
*/
,enrollment_progress AS (
    SELECT
        cp.[partner_user_id]
        ,course_id
        ,MIN(course_progress_ts)::DATE AS activity_first_dt
        ,MAX(course_progress_ts)::DATE AS activity_last_dt   
        ,COUNT(DISTINCT course_progress_ts::DATE) AS num_days_active
    FROM course_progress AS cp -- contains 'started' or 'completed' progress
    GROUP BY 1,2    
) 

/*
Learners who complete the course are logged by reaching one of two passing
states in the the course_grades table. Generate when they first pass.
*/
,enrollment_completed AS (
    SELECT
        cg.[partner_user_id]
        ,course_id
        ,MIN(course_grade_ts)::DATE AS completion_dt
    FROM course_grades AS cg -- contains when the learner reached the highest grade
    WHERE
        course_passing_state_id IN (1,2) -- 'passed' or 'verified passed' states
    GROUP BY 1,2    
) 

/*
Learners can own the course, either by payment or receiving financial aid.
*/
,enrollment_ownership AS (
    SELECT
        uccp.[partner_user_id]
        ,course_id
        ,was_payment OR was_finaid_grant AS was_paid_or_finaid
    FROM users_courses__certificate_payments AS uccp
)

/*
Combine all learner-course stats into one final table.
*/
SELECT
    ec.[partner_user_id]
    ,course_id
    ,commenced_dt
    ,activity_first_dt IS NOT NULL AS is_enrollment_active
    ,activity_first_dt
    ,activity_last_dt    
    ,num_days_active
    ,completion_dt IS NOT NULL AS is_enrollment_completed
    ,completion_dt
    ,COALESCE(was_paid_or_finaid, FALSE) AS was_paid_or_finaid
FROM enrollment_commenced AS ec
LEFT JOIN enrollment_progress
    USING ([partner_user_id], course_id)
LEFT JOIN enrollment_completed
    USING ([partner_user_id], course_id)
LEFT JOIN enrollment_ownership
    USING ([partner_user_id], course_id)

