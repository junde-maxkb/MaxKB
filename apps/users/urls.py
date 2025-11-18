from django.urls import path

from . import views
from .views import OauthCallbackView, AuthConnect, SSOLoginCallbackView

app_name = "user"
urlpatterns = [
    path('profile', views.Profile.as_view()),
    path('user', views.User.as_view(), name="profile"),
    path('user/language', views.SwitchUserLanguageView.as_view(), name='language'),
    path('user/list', views.User.Query.as_view()),
    path('user/login', views.Login.as_view(), name='login'),
    path('user/logout', views.Logout.as_view(), name='logout'),
    # path('user/register', views.Register.as_view(), name="register"),
    path("user/send_email", views.SendEmail.as_view(), name='send_email'),
    path("user/check_code", views.CheckCode.as_view(), name='check_code'),
    path("user/re_password", views.RePasswordView.as_view(), name='re_password'),
    path("user/current/send_email", views.SendEmailToCurrentUserView.as_view(), name="send_email_current"),
    path("user/current/reset_password", views.ResetCurrentUserPasswordView.as_view(), name="reset_password_current"),
    path("user_manage", views.UserManage.as_view(), name="user_manage"),
    path("user_manage/<str:user_id>", views.UserManage.Operate.as_view(), name="user_manage_operate"),
    path("user_manage/<str:user_id>/re_password", views.UserManage.RePassword.as_view(),
         name="user_manage_re_password"),
    path("user_manage/<str:user_id>/set_admin", views.UserManage.SetAdminManage.as_view(), name='set_admin'),
    path("user_manage/<int:current_page>/<int:page_size>", views.UserManage.Page.as_view(),
         name="user_manage_re_password"),
    path('user/list/<str:type>', views.UserListView.as_view()),
    path('github_auth/', AuthConnect.as_view(), name='github_auth'),
    path('oauth_callback/', OauthCallbackView.as_view(), name='oauth_callback'),
    path('sso_callback/', SSOLoginCallbackView.as_view(), name='sso_callback'),

    path('chat_history/<str:user_id>', views.ChatHistoryView.List.as_view(), name='chat_history_list'),
    path('chat_history/<str:user_id>/<int:current_page>/<int:page_size>', views.ChatHistoryView.Page.as_view(),
         name='chat_history_page'),
    path('chat_history', views.ChatHistoryView.Save.as_view(), name='chat_history_save'),
    path('chat_message', views.ChatMessageView.Save.as_view(), name='chat_message_save'),
    path('chat_message/batch', views.ChatMessageView.Batch.as_view(), name='chat_message_batch'),
    path('chat_message/list', views.ChatMessageView.List.as_view(), name='chat_message_list'),
]
