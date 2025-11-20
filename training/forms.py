# Django forms for Training app
from django import forms
from .models import Training, ModuleType, TrainingStatus, TrainingTypeChoices
from oppia.models.main import Course
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div
from django.urls import reverse
from django.utils.translation import gettext as _

class TrainingForm(forms.ModelForm):
	class Meta:
		model = Training
		fields = [
			'name',
			'description',
			'date',
			'sponsor',
			'module_type',
			'training_center',
			'training_type',
			'courses',
		]
		widgets = {
			'date': forms.DateInput(attrs={'type': 'date'}),
			'training_type': forms.Select(choices=TrainingTypeChoices.choices),
			'courses': forms.SelectMultiple(),
		}
		labels = {
            'training_type': 'Type of Training',
        }

class EditTrainingForm(forms.ModelForm):
	class Meta:
		model = Training
		fields = [
			'name',
			'description',
			'date',
			'sponsor',
			'module_type',
			'status',
			'training_center',
			'training_type',
		]
		widgets = {
			'date': forms.DateInput(attrs={'type': 'date'}),
			'status': forms.RadioSelect(choices=TrainingStatus.choices),
			'training_type': forms.Select(choices=TrainingTypeChoices.choices),
		}
		labels = {
			'training_type': 'Type of Training',
		}

class ModuleTypeForm(forms.ModelForm):
	class Meta:
		model = ModuleType
		fields = [
			'name',
			'description',
			'code',
		]

class AddParticipantForm(forms.Form):
	user = forms.ModelChoiceField(queryset=None, label='Select User')

	def __init__(self, *args, **kwargs):
		training = kwargs.pop('training', None)
		super().__init__(*args, **kwargs)
		base_qs = User.objects.filter(is_staff=False)
		if training:
			# Exclude users already associated with the training and admin users
			self.fields['user'].queryset = base_qs.exclude(trainings=training)
		else:
			self.fields['user'].queryset = base_qs

class AddCourseForm(forms.Form):
	course = forms.ModelChoiceField(queryset=Course.objects.all(), label='Select Course')

	def __init__(self, *args, **kwargs):
		training = kwargs.pop('training', None)
		course = kwargs.pop('course', None)
		super().__init__(*args, **kwargs)
		self.fields['course'].queryset = Course.objects.all()
		if training:
			self.fields['course'].queryset = self.fields['course'].queryset.exclude(trainings=training)

class UploadPartcipantsProfileForm(forms.Form):
	upload_file = forms.FileField(
		required=True,
		error_messages={'required': _('Please select a file to upload')}, )

	only_update = forms.BooleanField(
		initial=True,
		required=False,
		label=_('Only update data'),
		help_text=_("If a user already exists, only missing/blank fields will "
					"be updated"))

	def __init__(self, *args, **kwargs):
		training_id = kwargs.pop('training_id', None)
		super(UploadPartcipantsProfileForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		if training_id:
			self.helper.form_action = reverse('training:bulk_add_participants', args=[training_id])
		else:
			self.helper.form_action = reverse('training:bulk_add_participants')
		self.helper.form_class = 'form-horizontal'
		self.helper.label_class = 'col-lg-3 col-md-4 col-sm-3'
		self.helper.field_class = 'col-lg-6 col-md-8 col-sm-6'
		self.helper.layout = Layout(
			'upload_file',
			'only_update',
			Div(
				Submit('submit', _(u'Upload'), css_class='btn btn-default'),
				css_class='col-lg-offset-2 col-lg-4',
			),
		)
