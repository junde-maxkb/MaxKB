SELECT 
    temp_application.*,
    to_json(dataset_setting) as dataset_setting,
    to_json(model_setting) as model_setting,
    to_json(work_flow) as work_flow,
    COALESCE(app_stats.chat_record_count, 0) as chat_record_count,
    COALESCE(app_stats.tokens_num, 0) as tokens_num,
    creator_user.username as creator_name
FROM ( 
    SELECT * FROM application ${application_custom_sql} 
    UNION
    SELECT *
    FROM application
    WHERE application.is_deleted = false AND application."id" IN ( 
        SELECT team_member_permission.target 
        FROM team_member team_member 
        LEFT JOIN team_member_permission team_member_permission ON team_member_permission.member_id = team_member."id" 
        ${team_member_permission_custom_sql}
    )
) temp_application
LEFT JOIN "user" creator_user ON creator_user.id = temp_application.user_id 
LEFT JOIN (
	SELECT
        application_chat.application_id,
        COUNT(application_chat_record.id) as chat_record_count,
        SUM(application_chat_record.message_tokens + application_chat_record.answer_tokens) as tokens_num
    FROM application_chat_record application_chat_record
    LEFT JOIN application_chat application_chat ON application_chat.id = application_chat_record.chat_id
    GROUP BY application_chat.application_id
) app_stats ON app_stats.application_id = temp_application.id
${default_sql}