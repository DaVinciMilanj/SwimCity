from django.contrib import admin
from .models import *


# Register your models here.


class PoolAdmin(admin.ModelAdmin):
    fields = ['name', 'address', 'status', 'active', 'gender']
    list_display = ['name', 'active', 'status', 'gender']


admin.site.register(Pool, PoolAdmin)


class CreateClassAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'pool', 'status', 'gender']
    search_fields = ['pool', 'status']
    fields = ['pool', 'status', 'gender']
    readonly_fields = ['gender']

    def save_model(self, request, obj, form, change):
        # تنظیم جنسیت بر اساس استخر انتخاب‌شده قبل از ذخیره
        if obj.pool:
            obj.gender = obj.pool.gender

        super().save_model(request, obj, form, change)


admin.site.register(CreateClass, CreateClassAdmin)


class ClassesAdmin(admin.ModelAdmin):
    list_display = ['course_start', 'teacher', 'start', 'end', 'start_clock', 'end_clock' ,'total_price','active']
    fields = ['course_start', 'teacher', 'start', 'end', 'start_clock', 'end_clock','price' ,'discount' ,'active']
    search_fields = ['course_start']


admin.site.register(Classes, ClassesAdmin)


class StartClassAdmin(admin.ModelAdmin):
    list_display = ['course', 'teacher','register_count' , 'limit_register']
    fields = ['course', 'student', 'register_count' , 'limit_register']

    def teacher(self , obj):
        return obj.course.teacher

    teacher.short_description = 'Teacher L-Name'
admin.site.register(StartClass, StartClassAdmin)


class PaidClassAdmin(admin.ModelAdmin):
    list_display = ['course' , 'user' , 'price']

    def price(self , obj):
        return obj.course.price

admin.site.register(Paid , PaidClassAdmin)