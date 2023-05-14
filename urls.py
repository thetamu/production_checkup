from django.urls import path

from .views import HomepageView, ProfileView, ProfileCreateView, JobsCreateView, ProfileSearchView, ProfileDeleteView, \
    JobsDeleteView, DetailCreateView, download_detail, select_mid, unselect_mid, take_permission, untake_permission, \
    select_sen, unselect_sen, detail_done, OrderInfoView, ProfileUpdateView, detail_update, DoneDetailArchiveView, \
    done_detail_archive

urlpatterns = [
    path('', HomepageView.as_view(), name='home'),
    path('profile/create_new_profile', ProfileCreateView.as_view()),
    path('profile/<int:pk>/update/', ProfileUpdateView.as_view()),
    path('job/create_jobs', JobsCreateView.as_view(), name='create_job'),
    path('profile/search/', ProfileSearchView.as_view(), name='search_user'),
    path('profile/<int:pk>/delete', ProfileDeleteView.as_view()),
    path('job/<int:pk>/delete', JobsDeleteView.as_view()),
    path('job/<int:pk>/delete', JobsDeleteView.as_view()),
    path('detail/upload', DetailCreateView.as_view()),
    path('detail/success', download_detail, name='uploaded'),
    path('order/<int:pk>', OrderInfoView.as_view(), name='order_info'),
    path('select_mid/<int:pk>', select_mid, name='select_mid'),
    path('profile/<int:pk>', ProfileView.as_view(), name='profile'),
    path('unselect_mid/<int:pk>', unselect_mid, name='unselect_mid'),
    path('take_permission/<int:pk>/<int:jpk>', take_permission, name='take_permission'),
    path('untake_permission/<int:pk>/<int:jpk>', untake_permission, name='untake_permission'),
    path('select_sen/<int:pk>', select_sen, name='select_sen'),
    path('unselect_sen/<int:pk>', unselect_sen, name='unselect_sen'),
    path('detail_done/<int:pk>', detail_done, name='detail_done'),
    path('detail_update/<int:pk>', detail_update, name='detail_update'),
    path('archive/<int:pk>', DoneDetailArchiveView.as_view()),
    path('archive_success', done_detail_archive, name='archive')
]
