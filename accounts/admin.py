from django.contrib import admin
from .models import *
from .forms import *
from django.contrib.auth.admin import UserAdmin


# Register your models here.


# class CustomUserAdmin(admin.ModelAdmin):
#     add_form = CustomUserCreationForm
#     form = CustomUserChangeForm
#     model = CustomUser
#     list_display = ['last_name', 'phone', 'username']
#     fieldsets = UserAdmin.fieldsets + (
#         (None, {'fields': ('code_meli',)}),
#         (None, {'fields': ('phone',)}),
#         (None, {'fields': ('birthday',)}),
#         (None, {'fields': ('status',)})
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         (None, {'fields': ('first_name',)}),
#         (None, {'fields': ('last_name',)}),
#         (None, {'fields': ('code_meli',)}),
#         (None, {'fields': ('phone',)}),
#         (None, {'fields': ('birthday',)}),
#         (None, {'fields': ('status',)})
#
#     )
#

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'phone', 'username']


admin.site.register(CustomUser, CustomUserAdmin)


class TeacherAdminShow(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone']
    readonly_fields = ['average_rate']


admin.site.register(Teacher, TeacherAdminShow)


class AdminTeacherFormShow(admin.ModelAdmin):
    list_display = ['user', 'phone_number']



admin.site.register(TeacherSignUpForm, AdminTeacherFormShow)

class TeacherRateUser(admin.ModelAdmin):
    list_display = ['user' , 'teacher' , 'rate']


admin.site.register(RateToTeacher , TeacherRateUser)