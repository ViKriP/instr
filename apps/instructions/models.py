from django.db import models


class Instruction(models.Model):
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Dependency(models.Model):
    # related_name='dependencies' позволяет обращаться: instruction.dependencies.all()
    instruction = models.ForeignKey(
        Instruction, related_name="dependencies", on_delete=models.CASCADE
    )
    name = models.CharField("Пакет/Зависимость", max_length=100)
    check_command = models.CharField("Команда проверки", max_length=200)


class Task(models.Model):
    instruction = models.ForeignKey(
        Instruction, related_name="tasks", on_delete=models.CASCADE
    )
    name = models.CharField("Название задачи", max_length=200)
    sequence = models.IntegerField("Порядковый номер", default=1)

    class Meta:
        ordering = ["sequence"]  # Автоматическая сортировка


class Solution(models.Model):
    task = models.ForeignKey(Task, related_name="solutions", on_delete=models.CASCADE)
    exec_command = models.TextField("Команда выполнения")
