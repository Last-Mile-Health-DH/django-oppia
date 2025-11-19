from django.urls import path
from .views import (training_list, module_type_list, add_module_type,
                    training_detail, module_type_detail, edit_module_type,
                    change_training_status, add_training, add_participant,
                    edit_training, BulkAddParticipants, remove_participant)

app_name = 'training'

urlpatterns = [
    path('trainings/', training_list, name='training_list'),
    path('module-types/', module_type_list, name='module_type_list'),
    path('trainings/<int:training_id>/', training_detail, name='training_detail'),
    path('module-types/<int:module_type_id>/', module_type_detail, name='module_type_detail'),
    path('trainings/<int:training_id>/status/<str:status>/', change_training_status, name='change_training_status'),
    path('trainings/add/', add_training, name='add_training'),
    path('trainings/<int:training_id>/edit/', edit_training, name='edit_training'),
    path('module-types/add/', add_module_type, name='add_module_type'),
    path('module-types/<int:module_type_id>/edit/', edit_module_type, name='edit_module_type'),
    path('trainings/<int:training_id>/add-participant/', add_participant, name='add_participant'),
    path('trainings/<int:training_id>/bulk-add-participants/', BulkAddParticipants.as_view(), name='bulk_add_participants'),
    path('trainings/<int:training_id>/remove-participant/<int:user_id>/', remove_participant, name='remove_participant'),
]