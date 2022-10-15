from threading import active_count
from turtle import onkeyrelease
from flet import (
    Checkbox,
    Column,
    FloatingActionButton,
    IconButton,
    OutlinedButton,
    Page,
    Row,
    Tab,
    Tabs,
    Text,
    TextField,
    UserControl,
    colors,
    icons,
); from backend import add, remove, edit, get, reload_db


#? TODO: Lint below code for better linking backend.


class Task(UserControl):
    def __init__(self, task_name: str, task_status_change, task_delete, task_id: int = -1, task_completion: bool = False):
        super().__init__()
        self.completion = task_completion
        self.task_name = task_name
        self._id = task_id
        if self._id < 11111:
            self.task_dict = add(task_name)
            self._id = self.task_dict["_id"]
        else:
            #* TODO: Using above parameters applying dot notation there instead of querying again, for more efficiency.
            self.task_dict = get({"_id": self._id})[0]
        self.task_status_change = task_status_change
        self.task_delete = task_delete

    def build(self):
        self.display_task = Checkbox(
            value=self.completion, label=self.task_name, on_change=self.status_changed
        )
        self.edit_name = TextField(expand=1)

        self.display_view = Row(
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.display_task,
                Row(
                    spacing=0,
                    controls=[
                        IconButton(
                            icon=icons.CREATE_OUTLINED,
                            tooltip="Edit To-Do",
                            on_click=self.edit_clicked,
                        ),
                        IconButton(
                            icons.DELETE_OUTLINE,
                            tooltip="Delete To-Do",
                            on_click=self.delete_clicked,
                        ),
                    ],
                ),
            ],
        )

        self.edit_view = Row(
            visible=False,
            alignment="spaceBetween",
            vertical_alignment="center",
            controls=[
                self.edit_name,
                IconButton(
                    icon=icons.DONE_OUTLINE_OUTLINED,
                    icon_color=colors.GREEN,
                    tooltip="Update To-Do",
                    on_click=self.save_clicked,
                ),
            ],
        )
        return Column(controls=[self.display_view, self.edit_view])

    def edit_clicked(self, e):
        self.edit_name.value = self.display_task.label
        self.display_view.visible = False
        self.edit_view.visible = True
        self.update()

    def save_clicked(self, e):
        self.display_task.label = self.edit_name.value
        self.task_name = self.display_task.label
        self.task_dict.name = self.task_name
        self._update_db()
        self.display_view.visible = True
        self.edit_view.visible = False
        self.update()

    def status_changed(self, e):
        self.completion = self.display_task.value
        self.task_dict.completed = self.completion
        self._update_db()
        self.task_status_change(self)

    def delete_clicked(self, e):
        #? INFO: Might need to delete task here.
        self.task_delete(self)

    def _update_db(self):
        edit(self.task_dict._id, self.task_dict.name, self.task_dict.completed)

    def __repr__(self) -> str:
        return str(self.task_dict)


class TodoApp(UserControl):
    def build(self):
        self.new_task = TextField(hint_text="What's another on the list #Gentleman?", expand=True, on_submit=self.new_task_submitted)

        self.filter = Tabs(
            selected_index=0,
            on_change=self.tabs_changed,
            tabs=[Tab(text="all"), Tab(text="active"), Tab(text="completed")],
        )

        self.load_list()

        #? INFO: App's root control (i.e. "view") containing all other controls.
        return Column(
            width=600,
            controls=[
                Row([Text(value="To-Do Manager for #Gentleman", style="headlineMedium")], alignment="center"),
                Row(
                    controls=[
                        self.new_task,
                        FloatingActionButton(icon=icons.ADD, on_click=self.add_clicked),
                    ],
                ),
                Column(
                    spacing=25,
                    controls=[
                        self.filter,
                        self.tasks,
                        Row(
                            alignment="spaceBetween",
                            vertical_alignment="center",
                            controls=[
                                self.items_left,
                                OutlinedButton(
                                    text="Refresh list", on_click=self.refresh_clicked
                                ),
                                OutlinedButton(
                                    text="Clear completed", on_click=self.clear_clicked
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        )

    def load_list(self):
        print("Loading list...")
        self.tasks = Column()
        _init_task_qty = 0
        for task_info in get():
            print(f"Appending task: {task_info}")
            task = Task(task_info.name, self.task_status_change, self.task_delete, task_info._id, task_info.completed)
            if task.completion:
                _init_task_qty += 1
            self.tasks.controls.append(task)
        print(f"Writing active tasks: {_init_task_qty}")
        self.items_left = Text(f"{_init_task_qty} active item(s) left.")

    def new_task_submitted(self, e):
        return self.add_clicked(e)

    def add_clicked(self, e):
        if self.new_task.value:
            task = Task(self.new_task.value, self.task_status_change, self.task_delete)
            self.tasks.controls.append(task)
            self.new_task.value = ""
            self.update()

    def task_status_change(self, task):
        self.update()

    def task_delete(self, task):
        remove(task._id)
        self.tasks.controls.remove(task)
        self.update()

    def tabs_changed(self, e):
        self.update()

    def refresh_clicked(self, e):
        #! TODO: FIX ME!!!
        print("Refresh pressed.")
        reload_db()
        self.load_list()
        self.update()

    def clear_clicked(self, e):
        for task in self.tasks.controls[:]:
            if task.completion is True:
                self.task_delete(task)

    def update(self):
        status = self.filter.tabs[self.filter.selected_index].text
        _active_tasks = 0
        for task in self.tasks.controls:
            task.visible = (
                status == "all"
                or (status == "active" and task.completion == False)
                or (status == "completed" and task.completion)
            )
            if task.completion is not True:
                _active_tasks += 1
        self.items_left.value = f"{_active_tasks} active item(s) left."
        super().update()


def index(page: Page):
    page.title = "#GentleToDoManager"
    page.horizontal_alignment = "center"
    page.scroll = "adaptive"
    page.update()
    app = TodoApp()
    page.add(app)


if __name__ == "__main__":
    __import__("flet").app(target=index)
