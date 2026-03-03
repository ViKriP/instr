from django.contrib import admin

from .models import Dependency, Instruction, Solution, Task


class TaskInline(admin.TabularInline):
    model = Task
    extra = 1


class DependencyInline(admin.TabularInline):
    model = Dependency
    extra = 1


@admin.register(Instruction)
class InstructionAdmin(admin.ModelAdmin):
    inlines = [DependencyInline, TaskInline]


admin.site.register(Solution)
