import tkinter as tk
import pickle
import re
from datetime import datetime, timedelta

class ClassInputDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("入力画面")

        self.class_name_label = tk.Label(self.dialog, text="科目名")
        self.class_name_entry = tk.Entry(self.dialog)
        self.class_name_label.pack()
        self.class_name_entry.pack()

        self.submit_button = tk.Button(self.dialog, text="OK", command=self.on_ok_button_clicked)
        self.submit_button.pack()

        self.class_name = ""

    def on_ok_button_clicked(self):
        class_name = self.class_name_entry.get()
        if len(class_name) > 20:
            self.show_warning("最大文字数を超えています")
        else:
            self.class_name = class_name
            self.dialog.destroy()

    def show_warning(self, message):
        warning_label = tk.Label(self.dialog, text=message, fg="red")
        warning_label.pack()

class AssignmentInputDialog:
    MAX_CHARACTERS = 20
    DATE_PATTERN = r"\d{1,2}/\d{1,2}"

    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("課題入力画面")

        self.assignment_name_label = tk.Label(self.dialog, text="課題名")
        self.assignment_name_entry = tk.Entry(self.dialog)
        self.assignment_name_label.pack()
        self.assignment_name_entry.pack()

        self.deadline_label = tk.Label(self.dialog, text="提出日")
        self.deadline_entry = tk.Entry(self.dialog)
        self.deadline_label.pack()
        self.deadline_entry.pack()

        self.submit_button = tk.Button(self.dialog, text="OK", command=self.on_ok_button_clicked)
        self.submit_button.pack()

        self.assignment_name = ""
        self.deadline = ""
        self.ok_clicked = False

    def on_ok_button_clicked(self):
        self.assignment_name = self.assignment_name_entry.get()
        self.deadline = self.deadline_entry.get()

        if len(self.assignment_name) > self.MAX_CHARACTERS:
            error_message = "最大文字数を超えています"
            error_message_label = tk.Label(self.dialog, text=error_message, fg="red")
            error_message_label.pack()
        elif not re.match(self.DATE_PATTERN, self.deadline):
            error_message = "提出日が指定された文字列ではありません"
            error_message_label = tk.Label(self.dialog, text=error_message, fg="red")
            error_message_label.pack()
        else:
            self.ok_clicked = True
            self.dialog.destroy()

class DeleteConfirmationDialog:
    def __init__(self, parent, row, col, subject_options_dialog=None, assignment_options_dialog=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("削除確認画面")

        delete_message = "本当に削除しますか？"
        delete_message_label = tk.Label(self.dialog, text=delete_message)
        delete_message_label.pack()

        delete_button = tk.Button(
            self.dialog,
            text="削除する",
            command=lambda: self.on_delete_button_clicked(
                row, col, subject_options_dialog, assignment_options_dialog
            ),
        )
        delete_button.pack()

    def on_delete_button_clicked(
        self, row, col, subject_options_dialog=None, assignment_options_dialog=None
    ):
        self.dialog.destroy()
        app.delete_data(row, col, subject_options_dialog, assignment_options_dialog)

class ReturnToTimetableConfirmationDialog:
    def __init__(self, parent, assignment_index, assignment_name, deadline, cell_row, cell_col):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("確認画面")

        confirmation_message = "選択した課題を時間割表に戻しますか？"
        confirmation_message_label = tk.Label(self.dialog, text=confirmation_message)
        confirmation_message_label.pack()

        return_button = tk.Button(
            self.dialog,
            text="時間割表に戻す",
            command=lambda: self.on_return_button_clicked(
                assignment_index, assignment_name, deadline, cell_row, cell_col
            ),
        )
        return_button.pack()

        cancel_button = tk.Button(self.dialog, text="キャンセル", command=self.dialog.destroy)
        cancel_button.pack()

    def on_return_button_clicked(
        self, assignment_index, assignment_name, deadline, cell_row, cell_col
    ):
        self.dialog.destroy()
        app.return_assignment_to_timetable(
            assignment_index, assignment_name, deadline, cell_row, cell_col
        )

class SelectScreenToChangeOrDelete:
    def __init__(self, parent, row, col, subject_options_dialog=None, assignment_options_dialog=None):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("選択画面")

        change_button = tk.Button(
            self.dialog,
            text="変更",
            command=lambda: self.show_edit_dialog(row, col),
        )
        delete_button = tk.Button(
            self.dialog,
            text="削除",
            command=lambda: self.show_delete_confirmation_dialog(
                row, col, subject_options_dialog, assignment_options_dialog
            ),
        )

        change_button.pack()
        delete_button.pack()

    def show_edit_dialog(self, row, col):
        if row % 2 == 0:  # 科目名のセル
            input_dialog = ClassInputDialog(self.dialog)
            self.dialog.wait_window(input_dialog.dialog)
            subject_name = input_dialog.class_name
            if subject_name:
                app.change_subject(row, col, subject_name)
        else:  # 課題のセル
            assignment_input_dialog = AssignmentInputDialog(self.dialog)
            self.dialog.wait_window(assignment_input_dialog.dialog)
            if assignment_input_dialog.ok_clicked:
                assignment_name = assignment_input_dialog.assignment_name
                deadline = assignment_input_dialog.deadline
                if assignment_name and deadline:
                    app.change_assignment(row, col, assignment_name, deadline)

    def show_delete_confirmation_dialog(self, row, col, subject_options_dialog=None, assignment_options_dialog=None):
        DeleteConfirmationDialog(self.dialog, row, col, subject_options_dialog, assignment_options_dialog)

class SelectScreenToChangeDeleteOrMove:
    def __init__(self, parent, row, col, assignment_options_dialog):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("選択画面")

        change_button = tk.Button(
            self.dialog,
            text="変更",
            command=lambda: self.show_edit_dialog(row, col),
        )
        delete_button = tk.Button(
            self.dialog,
            text="削除",
            command=lambda: self.show_delete_confirmation_dialog(row, col, assignment_options_dialog),
        )
        move_button = tk.Button(
            self.dialog,
            text="提出済みに移動",
            command=lambda: self.move_assignment_to_submitted(row, col, assignment_options_dialog),
        )

        change_button.pack()
        delete_button.pack()
        move_button.pack()

    def show_edit_dialog(self, row, col):
        assignment_input_dialog = AssignmentInputDialog(self.dialog)
        self.dialog.wait_window(assignment_input_dialog.dialog)
        assignment_name = assignment_input_dialog.assignment_name
        deadline = assignment_input_dialog.deadline
        if assignment_input_dialog.ok_clicked:
            app.change_assignment(row, col, assignment_name, deadline)

    def show_delete_confirmation_dialog(self, row, col, assignment_options_dialog):
        DeleteConfirmationDialog(self.dialog, row, col, assignment_options_dialog)

    def move_assignment_to_submitted(self, row, col, assignment_options_dialog):
        app.move_assignment_to_submitted(row, col)
        assignment_options_dialog.destroy()

class TimetableScreen:
    def __init__(self, root):
        self.root = root
        self.labels = []
        self.data = [[{"subject": "", "assignment": "", "deadline": ""} for _ in range(5)] for _ in range(12)]
        self.submitted_data = []
        self.submitted_data_max_age = timedelta(days=7)  # 提出済み欄での課題の保持期間
        days = ["月", "火", "水", "木", "金"]
        limits = ["1", "", "2", "", "3", "", "4", "", "5", "", "6", ""]
        for col, day in enumerate(days):
            label = tk.Label(root, text=day, relief="solid", padx=10, pady=10, width=10)  # 幅を調整
            label.grid(row=0, column=col + 1, sticky="nsew")
        for row, limit in enumerate(limits):
            label = tk.Label(root, text=limit, relief="solid", padx=10, pady=10, width=10)  # 幅を調整
            label.grid(row=row + 1, column=0, sticky="nsew")

        for row in range(12):
            label_row = []
            for col in range(5):
                label = tk.Label(root, text=self.data[row][col]["subject"], relief="solid", padx=10, pady=10, width=20)  # 幅を調整
                label.grid(row=row + 1, column=col + 1, sticky="nsew")
                label.bind("<Button-1>", lambda event, row=row, col=col: self.handle_cell_click(row, col))
                label_row.append(label)
            self.labels.append(label_row)

        self.submitted_data_label = tk.Listbox(root, relief="solid", width=40)
        self.submitted_data_label.grid(row=13, column=0, columnspan=6, sticky="nsew", padx=10, pady=10)
        self.submitted_data_label.bind("<Button-1>", self.on_submitted_data_clicked)

    def handle_cell_click(self, row, col):
        if row % 2 == 0:  # 科目名のセル
            if self.data[row][col]["subject"]:
                self.show_subject_options(row, col)
            else:
                input_dialog = ClassInputDialog(self.root)
                self.root.wait_window(input_dialog.dialog)
                subject_name = input_dialog.class_name
                if subject_name:
                    self.data[row][col]["subject"] = subject_name
                    self.labels[row][col].configure(text=subject_name)
                    self.save_data()
        else:  # 課題のセル
            if self.data[row][col]["assignment"]:
                self.show_assignment_options(row, col)  # 課題が登録されているセルの場合にのみ選択画面を表示
            else:
                assignment_input_dialog = AssignmentInputDialog(self.root)
                self.root.wait_window(assignment_input_dialog.dialog)
                if assignment_input_dialog.ok_clicked:
                    assignment_name = assignment_input_dialog.assignment_name
                    deadline = assignment_input_dialog.deadline
                    if assignment_name and deadline:
                        self.data[row][col]["assignment"] = assignment_name
                        self.data[row][col]["deadline"] = deadline

                        remaining_days = self._calculate_remaining_days(deadline)
                        text = f"{assignment_name}\n{deadline}"
                        if remaining_days is not None and remaining_days < 2:
                            self.labels[row][col].configure(text=text, fg="red")
                        else:
                            self.labels[row][col].configure(text=text, fg="green")

                        self.save_data()
    
    def show_delete_confirmation_dialog(self, row, col):
        SelectScreenToChangeOrDelete(self.root, row, col)
                        
    def on_submitted_data_clicked(self, event):
        selection = self.submitted_data_label.curselection()
        if selection:
            assignment_index = selection[0]
            assignment = self.submitted_data[assignment_index]
            assignment_name = assignment["assignment"]
            deadline = assignment["deadline"]
            confirmation_dialog = ReturnToTimetableConfirmationDialog(
                self.root,
                assignment_index,
                assignment_name,
                deadline,
                assignment["cell_row"],
                assignment["cell_col"],
            )
            self.root.wait_window(confirmation_dialog.dialog)

    def show_subject_options(self, row, col):
        subject_options_dialog = SelectScreenToChangeOrDelete(self.root, row, col)

    def show_assignment_options(self, row, col):
        assignment_options_dialog = tk.Toplevel(self.root)
        assignment_options_dialog.title("選択画面")

        edit_button = tk.Button(
            assignment_options_dialog,
            text="課題内容の変更",
            command=lambda: self.show_edit_assignment_dialog(row, col),
        )
        delete_button = tk.Button(
            assignment_options_dialog,
            text="課題の削除",
            command=lambda: self.show_delete_confirmation_dialog(
                row, col, assignment_options_dialog
            ),
        )
        move_button = tk.Button(
            assignment_options_dialog,
            text="提出済みに移動",
            command=lambda: self.move_assignment_to_submitted(
                row, col, assignment_options_dialog
            ),
        )

        edit_button.pack()
        delete_button.pack()
        move_button.pack()

        assignment_options_dialog.protocol(
            "WM_DELETE_WINDOW", assignment_options_dialog.destroy
        )

        return assignment_options_dialog 
    
    def move_assignment_to_submitted(self, row, col):
        assignment_name, deadline = self.data[row][col]["assignment"], self.data[row][col]["deadline"]
        if assignment_name and deadline:
            self.submitted_data.append(
                {"assignment": assignment_name, "deadline": deadline, "cell_row": row, "cell_col": col}
            )
            self.data[row][col]["assignment"] = ""
            self.data[row][col]["deadline"] = ""
            self.labels[row][col].configure(text="", fg="black")
            self.update_submitted_data_label()
            self.save_data()

    def show_edit_assignment_dialog(self, row, col):
        assignment_input_dialog = AssignmentInputDialog(self.root)
        self.root.wait_window(assignment_input_dialog.dialog)
        assignment_name = assignment_input_dialog.assignment_name
        deadline = assignment_input_dialog.deadline
        if assignment_input_dialog.ok_clicked:
            self.update_assignment(row, col, assignment_name, deadline)

    def change_subject(self, row, col, subject_name):
        self.data[row][col]["subject"] = subject_name
        self.labels[row][col].configure(text=subject_name)
        self.save_data()
    
    def delete_data(self, row, col, subject_options_dialog=None, assignment_options_dialog=None):
        if row % 2 == 0:  # Delete subject
            self.data[row][col]["subject"] = ""
            self.labels[row][col].configure(text="")
        else:  # Delete assignment
            self.data[row][col] = {"subject": "", "assignment": "", "deadline": ""}
            self.labels[row][col].configure(text="")
        if subject_options_dialog:
            subject_options_dialog.destroy()
        if assignment_options_dialog:
            assignment_options_dialog.destroy()
        self.save_data()

    def save_data(self):
        with open("timetable_data.pkl", "wb") as f:
            pickle.dump(self.data, f)
        with open("submitted_data.pkl", "wb") as f:
            pickle.dump(self.submitted_data, f)

    def load_data(self):
        try:
            with open("timetable_data.pkl", "rb") as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.data = [[{"subject": "", "assignment": "", "deadline": ""} for _ in range(5)] for _ in range(12)]

        try:
            with open("submitted_data.pkl", "rb") as f:
                self.submitted_data = pickle.load(f)
        except FileNotFoundError:
            self.submitted_data = []

        for row in range(12):
            for col in range(5):
                subject = self.data[row][col]["subject"]
                assignment = self.data[row][col]["assignment"]
                deadline = self.data[row][col]["deadline"]
                if row % 2 == 0:
                    self.labels[row][col].configure(text=subject)
                else:
                    self.labels[row][col].configure(text=assignment + "\n" + deadline)

                remaining_days = self._calculate_remaining_days(deadline)
                self.update_cell_text_color(row, col, remaining_days)

        self.update_submitted_data_label()


    def _calculate_remaining_days(self, deadline):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        try:
            deadline_date = datetime.strptime(deadline, "%m/%d")
            deadline_date = deadline_date.replace(year=today.year)
            if today > deadline_date:
                deadline_date = deadline_date.replace(year=today.year + 1)
            remaining_days = (deadline_date - today).days
            return remaining_days
        except ValueError:
            return None
        


class InputClassControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def handle_input_class(self, class_name):
        self.timetable.add_class(self.cell_row, self.cell_col, class_name)

class ChangeOfClassControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def handle_change_class(self, class_name):
        self.timetable.update_class(self.cell_row, self.cell_col, class_name)

class DeleteClassControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def handle_delete_class(self):
        self.timetable.delete_class(self.cell_row, self.cell_col)

class InputAssignmentControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def handle_input_assignment(self, assignment_name, deadline):
        self.timetable.add_assignment(self.cell_row, self.cell_col, assignment_name, deadline)

class ChangeOfAssignmentControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def handle_change_assignment(self, assignment_name, deadline):
        self.timetable.update_assignment(self.cell_row, self.cell_col, assignment_name, deadline)

class DeleteAssignmentControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def handle_delete_assignment(self):
        self.timetable.delete_assignment(self.cell_row, self.cell_col)

class MoveAssignmentControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def handle_move_assignment(self):
        self.timetable.move_assignment_to_submitted(self.cell_row, self.cell_col)

class ReturnAssignmentControl:
    def __init__(self, timetable, assignment_index, assignment_name, deadline, cell_row, cell_col):
        self.timetable = timetable
        self.assignment_index = assignment_index
        self.assignment_name = assignment_name
        self.deadline = deadline
        self.cell_row = cell_row
        self.cell_col = cell_col

    def handle_return_assignment(self):
        self.timetable.return_assignment_to_timetable(
            self.assignment_index, self.assignment_name, self.deadline, self.cell_row, self.cell_col
        )

    def __init__(self, root):
        self.root = root

    def return_assignment_to_timetable(
        self, assignment_index, assignment_name, deadline, cell_row, cell_col
    ):
        timetable_screen.return_assignment_to_timetable(
            assignment_index, assignment_name, deadline, cell_row, cell_col
        )


class Timetable:
    def __init__(self):
        self.data = [['' for _ in range(7)] for _ in range(7)]
        self.submitted_list = []

    def add_subject(self, row, col, subject_name):
        self.data[row][col] = subject_name

    def add_assignment(self, row, col, assignment_name, deadline):
        self.data[row][col] = (assignment_name, deadline)

    def delete_data(self, row, col):
        self.data[row][col] = ''

    def update_subject(self, row, col, subject_name):
        self.data[row][col] = subject_name

    def update_assignment(self, row, col, assignment_name, deadline):
        self.data[row][col] = (assignment_name, deadline)

    def get_data(self, row, col):
        return self.data[row][col]

    def move_assignment_to_submitted(self, row, col):
        assignment_name, deadline = self.data[row][col]
        if assignment_name and deadline:
            self.submitted_list.append(Submitted(assignment_name, deadline))
            self.data[row][col] = ''

    def get_submitted_list(self):
        return self.submitted_list
    

class Class:
    def __init__(self, name):
        self.name = name


class Assignment:
    def __init__(self, name, deadline):
        self.name = name
        self.deadline = deadline


class Submitted:
    def __init__(self, name, deadline):
        self.name = name
        self.deadline = deadline

    def __str__(self):
        return f"Name: {self.name}, Deadline: {self.deadline}"

if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableScreen(root)
    root.mainloop()
