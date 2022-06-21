# -*- coding: utf-8 -*-
"""
"""

from django.urls import path
from . import views
from odk.openrosa import view_pull, view_push 

__author__ = 'jean pierre huart, patrick houben'
__email__ = 'j.huart@cra.wallonie.be, p.houben@cra.wallonie.be'
__copyright__ = 'Copyright 2021, Jean Pierre Huart'
__license__ = 'GPLv3'
__date__ = '2021-07-20'
__version__ = '0.2 dev'
__status__ = 'Development'


app_name = 'odk'

urlpatterns = [
    path('', views.home, name='home'),
    path('formList/', view_push.rosa_list, name='rosa_list'),
    path('form/<form_id>/', view_push.rosa_detail, name='rosa_detail'),
    path('submission', view_pull.xform_submit, name='rosa_submit'),

    path('list/', views.XFormListView.as_view(), name='xform_list'),
    path('<int:pk>/', views.XFormDetailView.as_view(), name='xform_detail'),
    path('<int:pk>/xls2xml', views.XFormDetailView.as_view(), name='xform_conv2xml'),
    path('<int:pk>/createmodel', views.XFormDetailView.as_view(), name='xform_createmodel'),
    path('add/', views.xform_upload, name='xform_add'),
    path('doc/', views.XFormTemplateView.as_view(), name='xform_doc'),
    # path('<int:pk>/upd', views.xform_upload, name='xform_upd'),
    path('<int:pk>/delete', views.XFormDelView.as_view(), name='xform_del'),

    path('submitted/', views.submittedfile_list, name='xformsubmit_list'),    
    path('submitted/<int:pk>/', views.XFormSubmitDetailView.as_view(), name='xformsubmit_detail'),
    path('submitted/<int:pk>/loaddata/', views.XFormSubmitDetailView.as_view(), name='xformsubmit_load'),
    path('submitted/<int:pk>/delete', views.XFormSubmitDelView.as_view(), name='xformsubmit_del'),    
]
