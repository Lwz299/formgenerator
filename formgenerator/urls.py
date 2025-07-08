from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_form_template, name='create_form'),
    path('add_fields/<int:form_id>/', views.add_fields, name='add_fields'),
    path('form/<int:form_id>/fill/', views.fill_form, name='fill_form'),
    path('form/<int:form_id>/preview/', views.preview_form, name='preview_form'),

    # AJAX routes
    path('ajax/delete_field/<int:field_id>/', views.ajax_delete_field, name='ajax_delete_field'),
    path('ajax/get_field/<int:field_id>/', views.ajax_get_field, name='ajax_get_field'),
    path('field/<int:field_id>/edit/', views.ajax_update_field, name='ajax_update_field'),
    path('form/<int:form_id>/submissions/', views.view_submissions, name='view_submissions'),
    path('confirm_delete_form/<int:form_id>/', views.delete_form_template, name='confirm_delete_form'),
    path('download_file/<int:value_id>/', views.download_base64_file, name='download_base64_file'),

]
