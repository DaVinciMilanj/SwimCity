from django.contrib import admin
from django.utils.timezone import localtime

from .models import *
from .forms import *
from django.db.models import Count
from django.contrib.auth.admin import UserAdmin


# Register your models here.

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'phone', 'username']
    search_fields = ['username', 'first_name', 'last_name', 'phone']  # این خط ضروری است


admin.site.register(CustomUser, CustomUserAdmin)


class TeacherAdminShow(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'phone']
    readonly_fields = ['average_rate']


admin.site.register(Teacher, TeacherAdminShow)


class AdminTeacherFormShow(admin.ModelAdmin):
    list_display = ['user', 'phone_number']


admin.site.register(TeacherSignUpForm, AdminTeacherFormShow)


class TeacherRateUser(admin.ModelAdmin):
    list_display = ['user', 'teacher', 'rate']


admin.site.register(RateToTeacher, TeacherRateUser)


@admin.register(CommentTeacher)
class CommentTeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'teacher', 'short_comment', 'total_reports', 'formatted_create')
    list_filter = ('teacher', 'user')
    search_fields = ('comment', 'user__username', 'teacher__name')
    ordering = ('-total_comment_report',)
    readonly_fields = ('total_reports',)

    def formatted_create(self, obj):
        return localtime(obj.create).strftime("%Y-%m-%d %H:%M")

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(total_reports=Count('comment_report'))

    def total_reports(self, obj):
        return obj.total_reports

    total_reports.admin_order_field = 'total_comment_report'
    total_reports.short_description = 'تعداد گزارشات'

    def short_comment(self, obj):
        return obj.comment[:50] + "..." if len(obj.comment) > 50 else obj.comment

    short_comment.short_description = "متن کامنت"
