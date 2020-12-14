from django.urls import path
from . import views
from django.conf.urls import url

app_name = 'vcn'

urlpatterns = [
    path('list/', views.TenancyListView.as_view(), name='tenancy_list'),
    path('tenancy/<int:pk>', views.TenancyDetailView.as_view(), name='tenancy_detail'),
    path('tenancy/new/', views.TenancyCreateView.as_view(), name='tenancy_new'),
    path('tenancy/<int:pk>/edit/', views.TenancyUpdateView.as_view(), name='tenancy_edit'),
    path('tenancy/<int:pk>/remove/', views.TenancyDeleteView.as_view(), name='tenancy_remove'),
    # path('tenancy/<int:pk>/updatekey/', views.PrivateKeyUpdateView.as_view(), name='tenancy_updatekey'),
    # path('tenancy/<int:pk>/generate/', views.GenerateTFView.as_view(), name='tenancy_generate')
]