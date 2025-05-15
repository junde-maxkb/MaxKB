import os

from django.urls import path

from . import views

app_name = "team"
urlpatterns = [
    path('team/member', views.TeamMember.as_view(), name="team"),
    # path('team/member/_batch', views.TeamMember.Batch.as_view()),
    path('team/member/<str:member_id>', views.TeamMember.Operate.as_view(), name='member'),
    path('team_manage/member', views.team_manage.TeamMember.as_view(), name="team_member"),
    path('team_manage/member/<str:member_id>', views.team_manage.TeamMember.Operate.as_view(),
         name='team_manage_member'),
    path('team_manage', views.team_manage.Team.as_view(), name="team_manage"),
    path('team_manage/<str:team_id>', views.team_manage.Team.Operate.as_view(), name='team_manage_operate'),
    path("team_manage/<str:team_id>/<int:current_page>/<int:page_size>", views.team_manage.Team.Page.as_view(),
         name="team_member_page_list"),
    path('team/user_teams', views.UserTeams.as_view(), name='user_teams'),
    path('team/shareable-list', views.ShareableList.as_view(), name='shareable_list'),
    path('provider/<str:provider>/<str:method>', views.Provide.Exec.as_view(), name='provide_exec'),
    path('provider', views.Provide.as_view(), name='provide'),
    path('provider/model_type_list', views.Provide.ModelTypeList.as_view(), name="provider/model_type_list"),
    path('provider/model_list', views.Provide.ModelList.as_view(),
         name="provider/model_name_list"),
    path('provider/model_params_form', views.Provide.ModelParamsForm.as_view(),
         name="provider/model_params_form"),
    path('provider/model_form', views.Provide.ModelForm.as_view(),
         name="provider/model_form"),
    path('model', views.Model.as_view(), name='model'),
    path('model/<str:model_id>/model_params_form', views.Model.ModelParamsForm.as_view(),
         name='model/model_params_form'),
    path('model/<str:model_id>', views.Model.Operate.as_view(), name='model/operate'),
    path('model/<str:model_id>/pause_download', views.Model.PauseDownload.as_view(), name='model/operate'),
    path('model/<str:model_id>/meta', views.Model.ModelMeta.as_view(), name='model/operate/meta'),
    path('email_setting', views.SystemSetting.Email.as_view(), name='email_setting'),
    path('login_auth_setting', views.SystemSetting.LoginAuth.as_view(), name='login_auth_setting'),
    path('valid/<str:valid_type>/<int:valid_count>', views.Valid.as_view())

]
if os.environ.get('SERVER_NAME', 'web') == 'local_model':
    urlpatterns += [
        path('model/<str:model_id>/embed_documents', views.ModelApply.EmbedDocuments.as_view(),
             name='model/embed_documents'),
        path('model/<str:model_id>/embed_query', views.ModelApply.EmbedQuery.as_view(),
             name='model/embed_query'),
        path('model/<str:model_id>/compress_documents', views.ModelApply.CompressDocuments.as_view(),
             name='model/embed_query'),
    ]
