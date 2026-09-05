from django.contrib import admin
from .models import InternshipTrack, TaskModule, UserTaskProgress


class TaskModuleInline(admin.TabularInline):
    model = TaskModule
    extra = 1


@admin.register(InternshipTrack)
class InternshipTrackAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TaskModuleInline]


@admin.register(TaskModule)
class TaskModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "track", "order")
    list_filter = ("track",)


@admin.register(UserTaskProgress)
class UserTaskProgressAdmin(admin.ModelAdmin):
    list_display = ("profile", "task", "is_completed", "completed_at")
    list_filter = ("is_completed",)
