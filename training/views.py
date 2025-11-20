from django.shortcuts import render, redirect, get_object_or_404
from .models import Training, ModuleType, TrainingStatus
from .forms import (TrainingForm, ModuleTypeForm, UploadPartcipantsProfileForm,
                    EditTrainingForm, AddParticipantForm, AddCourseForm)

from django.contrib.auth.models import User
from helpers.mixins.PermissionMixins import AdminRequiredMixin, StaffRequiredMixin
from django.views.generic import FormView, TemplateView, ListView
from profile.forms import UploadProfileForm, UserSearchForm, DeleteAccountForm, RegisterForm
from profile.models import UserProfile, CustomField, UserProfileCustomField
import csv
from django.utils.translation import gettext as _
from django.core.paginator import Paginator
from oppia.models.main import Course

# Create your views here.

def training_list(request):
    trainings = Training.objects.all().order_by('date')
    return render(request, 'training/training_list.html', {'trainings': trainings})

def module_type_list(request):
    module_types = ModuleType.objects.all().order_by('name')
    return render(request, 'training/module_type_list.html', {'module_types': module_types})

def add_module_type(request):
    if request.method == 'POST':
        form = ModuleTypeForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to module type list or detail page after saving
            return redirect('training:module_type_list')
    else:
        form = ModuleTypeForm()
    return render(request, 'training/add_module_type.html', {'form': form})

def training_detail(request, training_id):
    training_statuses = TrainingStatus.choices
    training = Training.objects.get(id=training_id)
    participants_list = training.get_participants()
    paginator = Paginator(participants_list, 10)  # Show 10 participants per page

    page_number = request.GET.get('page')
    participants = paginator.get_page(page_number)
    courses = training.courses.all()
    return render(request, 'training/training_detail.html', {
        'training': training,
        'training_statuses': training_statuses,
        'participants': participants,
        'courses': courses
    })

def module_type_detail(request, module_type_id):
    module_type = ModuleType.objects.get(id=module_type_id)
    trainings = module_type.trainings.all()
    return render(request, 'training/module_type_detail.html', {'module_type': module_type, 'trainings': trainings})

def edit_module_type(request, module_type_id):
    module_type = ModuleType.objects.get(id=module_type_id)
    if request.method == 'POST':
        form = ModuleTypeForm(request.POST, instance=module_type)
        if form.is_valid():
            form.save()
            # Redirect to module type detail page after saving
            return redirect('training:module_type_detail', module_type_id=module_type.id)
    else:
        form = ModuleTypeForm(instance=module_type)
    return render(request, 'training/edit_module_type.html', {'form': form})

def change_training_status(request, training_id, status):
    training = Training.objects.get(id=training_id)
    training.status = status
    training.save()
    return render(request, 'training/training_detail.html', {'training': training})

def add_training(request):
    if request.method == 'POST':
        form = TrainingForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to training list or detail page after saving
            return redirect('training:training_list')
    else:
        form = TrainingForm()
    return render(request, 'training/add_training.html', {'form': form})

def edit_training(request, training_id):
    training = Training.objects.get(id=training_id)
    training_statuses = TrainingStatus.choices
    if request.method == 'POST':
        form = EditTrainingForm(request.POST, instance=training)
        if form.is_valid():
            form.save()
            # Redirect to training detail page after saving
            return redirect('training:training_detail', training_id=training.id)
    else:
        form = TrainingForm(instance=training)
    return render(request, 'training/training_edit.html', {
        'form': form, 
        'training': training,
        'training_statuses': training_statuses})

def add_participant(request, training_id):
    training = Training.objects.get(id=training_id)
    participants = training.get_participants()
    if request.method == 'POST':
        form = AddParticipantForm(request.POST, training=training)
        if form.is_valid():
            user = form.cleaned_data['user']
            training.users.add(user)
            return redirect('training:training_detail', training_id=training.id)
    else:
        form = AddParticipantForm(training=training)
    return render(request, 'training/add_participant.html', {
        'form': form,
        'training': training,
        'participants': participants
    })

def add_course(request, training_id):
    training = Training.objects.get(id=training_id)
    courses = training.courses.all()
    if request.method == 'POST':
        form = AddCourseForm(request.POST, training=training)
        if form.is_valid():
            course = form.cleaned_data['course']
            training.courses.add(course)
        return redirect('training:training_detail', training_id=training.id)
    else:
        form = AddCourseForm(training=training)
    return render(request, 'training/add_course.html', {
        'training': training,
        'form': form,
        'courses': courses
    })
class BulkAddParticipants(AdminRequiredMixin, FormView):
    form_class = UploadPartcipantsProfileForm
    template_name = 'training/upload_participants.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['training_id'] = self.training.id
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.training = get_object_or_404(Training, pk=kwargs.get('training_id'))
        print("Training:", self.training.name)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        required_fields = ['username', 'firstname', 'lastname']
        only_update = form.cleaned_data.get('only_update', False)
        csv_file = csv.DictReader(
            chunk.decode('utf-8-sig') for chunk in self.request.FILES['upload_file'])

        context = self.get_context_data(form=form)
        context['results'] = self.process_upload_user_file(csv_file,
                                                           required_fields,
                                                           only_update)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["custom_fields"] = CustomField.objects.all().order_by('order')
        return context

    def process_upload_user_file(self, csv_file, required_fields, only_update):
        results = []
        try:
            for row in csv_file:
                # check all required fields defined
                all_defined = True
                for rf in required_fields:
                    if rf not in row or row[rf].strip() == '':
                        result = {
                            'username': row.get('username', None),
                            'created': False,
                            'message': _(u'No %s set' % rf)
                        }
                        results.append(result)
                        all_defined = False

                if not all_defined:
                    continue

                results.append(
                    self.process_upload_file_save_user(row, not only_update))

        except Exception as e:
            print("Error processing file:", e)  # Add this for debugging
            result = {
                'username': None,
                'created': False,
                'message': _(u'Could not parse file')
            }
            results.append(result)

        return results

    def process_upload_file_save_user(self, row, override_fields):
        user, user_created = User.objects.get_or_create(username=row['username'])

        password, autogenerated = self.update_user_fields(user, row, override_fields)
        self.update_user_profile(user, row, override_fields)
        self.update_custom_fields(user, row, override_fields)


        result = {
            'created': user_created,
            'username': row['username'],
        }
        if autogenerated and user_created:
            result['message'] = _(u'User created with password: %s' % password)
        elif not autogenerated and user_created:
            result['message'] = _(u'User created')
        elif autogenerated and not user_created:
            result['message'] = _(u'User updated with password: %s' % password)
        else:
            result['message'] = _(u'User updated')
        
        # Add user to training
        self.training.users.add(user)
        self.training.save()

        return result

    def update_user_fields(self, user, row, override_fields):
        if override_fields or not user.first_name:
            user.first_name = row['firstname']
        if override_fields or not user.last_name:
            user.last_name = row['lastname']

        if 'email' in row and (override_fields or not user.email):
            user.email = row['email']

        password = None
        auto_password = False

        # Only set password if the user doesn't have already one
        if not user.password or not user.has_usable_password():
            password = row.get('password', None)
            if not password:
                password = User.objects.make_random_password()
                auto_password = True
            user.set_password(password)

        user.save()
        return password, auto_password

    def update_user_profile(self, user, row, override_fields):
        up, created = UserProfile.objects.get_or_create(user=user)
        for col_name in row:
            if override_fields or (hasattr(up, col_name)
                                   and not getattr(up, col_name)):
                setattr(up, col_name, row[col_name])
        up.save()

    def update_custom_fields(self, user, row, override_fields):
        custom_fields = CustomField.objects.all()
        for cf in custom_fields:
            if cf.id in row:
                upcf, created = UserProfileCustomField.objects.get_or_create(
                    user=user, key_name=cf)
                if cf.type == 'bool':
                    if override_fields or upcf.value_bool is None:
                        upcf.value_bool = row[cf.id]
                elif cf.type == 'int':
                    if override_fields or not upcf.value_int:
                        upcf.value_int = row[cf.id]
                else:
                    if override_fields or not upcf.value_str:
                        upcf.value_str = row[cf.id]
                upcf.save()

def remove_participant(request, training_id, user_id):
    training = Training.objects.get(id=training_id)
    user = User.objects.get(id=user_id)
    training.users.remove(user)
    return redirect('training:training_detail', training_id=training.id)

def remove_course(request, training_id, course_id):
    training = Training.objects.get(id=training_id)
    course = Course.objects.get(id=course_id)
    training.courses.remove(course)
    return redirect('training:training_detail', training_id=training.id)
