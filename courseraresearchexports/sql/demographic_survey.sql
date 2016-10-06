/*
demographic_survey
This query partially denormalizes the demographics tables to create aggregate
information about the users in the present data export.

Columns
coursera_user_id
demographic_survey_submission_dt
demographic_survey_gender
demographic_survey_age
demographic_survey_country_cd_of_birth
demographic_survey_us_postal_code
demographic_survey_spanish_hispanic_or_latino_descent
demographic_survey_race
demographic_survey_highest_level_of_schooling
demographic_survey_currently_enrolled_in_an_educational_program
demographic_survey_level_of_current_educational_program
demographic_survey_subject_area_of_degree
demographic_survey_current_employment_status
demographic_survey_area_of_industry_currently_employed_in
demographic_survey_english_proficiency
demographic_survey_other_languages_spoken
*/

SELECT
    a.[demographics_user_id]
    ,MAX(a.submission_ts::DATE) AS demographic_survey_submission_dt
    ,MAX(CASE WHEN a.question_id = 11
        THEN c.choice_desc END) AS demographic_survey_gender
    ,MAX(CASE WHEN a.question_id = 12
        THEN DATE_PART('y', CURRENT_DATE) - a.answer_int END) AS demographic_survey_age
    ,UPPER(LEFT(MAX(CASE WHEN a.question_id = 13
        THEN c.choice_desc END), 2)) AS demographic_survey_country_cd_of_birth
    ,MAX(CASE WHEN a.question_id = 15
        THEN a.answer_int END) AS demographic_survey_us_postal_code
    ,MAX(CASE WHEN a.question_id = 16
        THEN c.choice_desc END) AS demographic_survey_spanish_hispanic_or_latino_descent
    ,RTRIM(STRING_AGG(CASE WHEN a.question_id = 17 THEN c.choice_desc END, ';')) AS demographic_survey_race
    ,MAX(CASE WHEN a.question_id = 18
        THEN c.choice_desc END) AS demographic_survey_highest_level_of_schooling
    ,MAX(CASE WHEN a.question_id = 19
        THEN c.choice_desc END) AS demographic_survey_currently_enrolled_in_an_educational_program
    ,MAX(CASE WHEN a.question_id = 20
        THEN c.choice_desc END) AS demographic_survey_level_of_current_educational_program
    ,RTRIM(STRING_AGG(CASE WHEN a.question_id = 21
        THEN c.choice_desc END, ';')) AS demographic_survey_subject_area_of_degree
    ,MAX(CASE WHEN a.question_id = 22
        THEN c.choice_desc END) AS demographic_survey_current_employment_status
    ,MAX(CASE WHEN a.question_id = 23
        THEN c.choice_desc END) AS demographic_survey_area_of_industry_currently_employed_in
    ,MAX(CASE WHEN a.question_id = 24
        THEN c.choice_desc END) AS demographic_survey_english_proficiency
    ,RTRIM(STRING_AGG(CASE WHEN a.question_id = 25
        THEN c.choice_desc END, ';')) AS demographic_survey_other_languages_spoken
FROM demographics_answers a
JOIN demographics_choices c USING (question_id, choice_id)
WHERE a.question_id BETWEEN 11 AND 25
    AND a.question_id = c.question_id
    AND a.choice_id = c.choice_id
GROUP BY 1
