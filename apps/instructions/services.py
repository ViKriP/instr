from .models import Dependency, Instruction, Solution, Task


# --- ИНСТРУКЦИИ ---
def get_all_instructions():
    """Возвращает список словарей для списка на главной"""
    return list(Instruction.objects.all().values("id", "name", "description"))


def get_full_instruction(inst_id):
    """Возвращает полную структуру со всеми вложенными данными"""
    try:
        inst = Instruction.objects.get(pk=inst_id)

        # Собираем зависимости
        deps = list(inst.dependencies.values("id", "name", "check_command"))

        # Собираем задачи вручную, чтобы достать solutions
        tasks_data = []
        for task in inst.tasks.all():
            # Берем решения для задачи
            solutions = list(task.solutions.values("id", "exec_command"))
            tasks_data.append(
                {
                    "id": task.id,
                    "name": task.name,
                    "sequence": task.sequence,
                    "solutions": solutions,
                }
            )

        return {
            "id": inst.id,
            "name": inst.name,
            "description": inst.description,
            "dependencies": deps,
            "tasks": tasks_data,
        }
    except Instruction.DoesNotExist:
        return None


def create_instruction(name, description):
    inst = Instruction.objects.create(name=name, description=description)
    return inst.id


def update_instruction(inst_id, name, description):
    Instruction.objects.filter(pk=inst_id).update(name=name, description=description)


def delete_instruction(inst_id):
    Instruction.objects.filter(pk=inst_id).delete()


# --- ЗАВИСИМОСТИ ---


def add_dependency(inst_id, name, check_command):
    Dependency.objects.create(
        instruction_id=inst_id, name=name, check_command=check_command
    )


def update_dependency(dep_id, name, check_command):
    Dependency.objects.filter(pk=dep_id).update(name=name, check_command=check_command)


def delete_dependency(dep_id):
    Dependency.objects.filter(pk=dep_id).delete()


# --- ЗАДАЧИ ---


def add_task_with_solution(inst_id, name, sequence, exec_command):
    # Создаем задачу
    task = Task.objects.create(instruction_id=inst_id, name=name, sequence=sequence)
    # Создаем дефолтное решение
    Solution.objects.create(task=task, exec_command=exec_command)


def update_task_with_solution(task_id, name, sequence, exec_command):
    # Обновляем задачу
    Task.objects.filter(pk=task_id).update(name=name, sequence=sequence)
    # Обновляем решение (предполагаем, что оно одно)
    # В реальном проекте тут нужна логика сложнее, но для старта пойдет
    task = Task.objects.get(pk=task_id)
    sol = task.solutions.first()
    if sol:
        sol.exec_command = exec_command
        sol.save()
    else:
        Solution.objects.create(task=task, exec_command=exec_command)


def delete_task(task_id):
    Task.objects.filter(pk=task_id).delete()
