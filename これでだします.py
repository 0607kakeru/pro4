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

        self.submit_button = tk.Button(self.dialog, text="完了", command=self.on_ok_button_clicked)
        self.submit_button.pack()

        self.class_name = ""

    def on_ok_button_clicked(self):
        class_name = self.class_name_entry.get()
        if len(class_name) > 20:
            message = "最大文字数を超えています"
            warning_label = tk.Label(self.dialog, text=message, fg="red")
            warning_label.pack()

        else:
            self.class_name = class_name
            self.dialog.destroy()


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

        self.submit_button = tk.Button(self.dialog, text="完了", command=self.on_ok_button_clicked)
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
    def __init__(self, parent, row, col, select_screen, assignment_options_dialog=None):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("削除確認画面")

        self.row = row
        self.col = col
        self.select_screen = select_screen
        self.assignment_options_dialog = assignment_options_dialog

        delete_message = "本当に削除しますか？"
        delete_message_label = tk.Label(self.dialog, text=delete_message)
        delete_message_label.pack()

        delete_button = tk.Button(
            self.dialog,
            text="削除する",
            command=self.on_delete_button_clicked,
        )
        delete_button.pack()

    def on_delete_button_clicked(self):
        self.dialog.destroy()
        app.delete_data(self.row, self.col, self.select_screen, self.assignment_options_dialog)


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
    def __init__(self, parent, row, col):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("選択画面")

        self.row = row
        self.col = col

        self.change_button = tk.Button(
            self.dialog,
            text="科目名の変更",
            command=lambda: self.select_change_button(row, col),
        )
        self.change_button.pack()

        self.delete_button = tk.Button(
            self.dialog,
            text="科目の削除",
            command=lambda: self.select_delete_button(row, col),
        )
        self.delete_button.pack()

    def select_change_button(self, row, col): 
        self.show_edit_dialog(row, col)

    def select_delete_button(self, row, col):
        self.show_delete_confirmation_dialog(row, col)

    def show_edit_dialog(self, row, col):
        input_dialog = ClassInputDialog(self.dialog)
        self.dialog.wait_window(input_dialog.dialog)
        subject_name = input_dialog.class_name
        if subject_name:
            app.change_subject(row, col, subject_name)
        self.dialog.destroy()

    def show_delete_confirmation_dialog(self, row, col):
        DeleteConfirmationDialog(self.dialog, row, col, self)


class SelectScreenToChangeDeleteOrMove:
    def __init__(self, parent, row, col):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("選択画面")

        self.row = row
        self.col = col
        
        self.change_button = tk.Button(
            self.dialog,
            text="課題内容の変更",
            command=lambda: self.select_change_button(row, col),
        )
        self.change_button.pack()
        
        self.delete_button = tk.Button(
            self.dialog,
            text="課題の削除",
            command=lambda: self.select_delete_button(row, col),
        )
        self.delete_button.pack()

        self.move_button = tk.Button(
            self.dialog,
            text="提出済みに移動",
            command=lambda: self.select_move_button(row, col),
        )
        self.move_button.pack()

    def select_change_button(self, row, col):
        self.show_edit_dialog(row, col)

    def select_delete_button(self, row, col):
        self.show_delete_confirmation_dialog(row, col)

    def select_move_button(self, row, col):
        app.move_assignment_to_submitted(row, col)
        self.dialog.destroy()        
        
    def show_edit_dialog(self, row, col):
        assignment_input_dialog = AssignmentInputDialog(self.dialog)
        self.dialog.wait_window(assignment_input_dialog.dialog)
        assignment_name = assignment_input_dialog.assignment_name
        deadline = assignment_input_dialog.deadline
        if assignment_input_dialog.ok_clicked:
            app.change_assignment(row, col, assignment_name, deadline)
        self.dialog.destroy()

    def show_delete_confirmation_dialog(self, row, col):
        DeleteConfirmationDialog(self.dialog, row, col, self)


class TimetableScreen:
    def __init__(self, root):
        self.root = root
        self.labels = []
        self.timetable = Timetable()
        self.submitted_data = []
        self.submitted_data_max_age = timedelta(days=7)  
        self.data = self.timetable.data

        for col, day in enumerate(Timetable.DAYS):
            label = tk.Label(root, text=day, relief="solid", padx=10, pady=10, width=10)  
            label.grid(row=0, column=col + 1, sticky="nsew")
        for row, limit in enumerate(Timetable.TIME_LIMITS):
            label = tk.Label(root, text=limit, relief="solid", padx=10, pady=10, width=10)  
            label.grid(row=row + 1, column=0, sticky="nsew")

        for row in range(12):
            label_row = []
            for col in range(5):
                label = tk.Label(root, text=self.timetable.data[row][col]["subject"], relief="solid", padx=10, pady=10, width=20)  # 幅を調整
                label.grid(row=row + 1, column=col + 1, sticky="nsew")
                label.bind("<Button-1>", lambda event, row=row, col=col: self.handle_cell_click(row, col))
                label_row.append(label)
            self.labels.append(label_row)

        self.submitted_data_label = tk.Listbox(root, relief="solid", width=40)
        self.submitted_data_label.grid(row=13, column=0, columnspan=6, sticky="nsew", padx=10, pady=10)
        self.submitted_data_label.bind("<Button-1>", self.on_submitted_data_clicked)

        self.load_data() 



    def handle_cell_click(self, row, col):
        if row % 2 == 0:  
            if self.data[row][col]["subject"]:
                self.show_subject_options(row, col)
            else:
                self.show_class_edit_dialog(row,col)
        else:  
            if self.data[row][col]["assignment"]:
                self.show_assignment_options(row, col)
            else:
                self.show_assignment_edit_dialog(row,col)
    
    def show_class_edit_dialog(self, row, col):
        input_dialog = ClassInputDialog(self.root)
        self.root.wait_window(input_dialog.dialog)
        subject_name = input_dialog.class_name
        if subject_name:
            self.data[row][col]["subject"] = subject_name
            self.labels[row][col].configure(text=subject_name)
            self.save_data()

    def show_assignment_edit_dialog(self, row, col):
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
                                                
    def on_submitted_data_clicked(self,selection):
        selection = self.submitted_data_label.curselection()
        if selection:
            self.show_return_confirmation_dialog(selection)
    
    def show_return_confirmation_dialog(self, selection):
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
        self.root.wait_window(subject_options_dialog.dialog)

    def show_assignment_options(self, row, col):
        assignment_options_dialog = SelectScreenToChangeDeleteOrMove(self.root, row, col)
        self.root.wait_window(assignment_options_dialog.dialog)

    def move_assignment_to_submitted(self, row, col, assignment_options_dialog=None):
        assignment_name, deadline = self.data[row][col]["assignment"], self.data[row][col]["deadline"]
        if assignment_name and deadline:
            self.submitted_data.append(
                {"assignment": assignment_name, "deadline": deadline, "cell_row": row, "cell_col": col}
            )
            self.data[row][col]["assignment"] = ""
            self.data[row][col]["deadline"] = ""
            self.labels[row][col].configure(text="", fg="black")
            self.update_submitted_data()
            self.save_data()
        if assignment_options_dialog:
            assignment_options_dialog.destroy()

    def change_subject(self, row, col, subject_name):
        self.data[row][col]["subject"] = subject_name
        self.labels[row][col].configure(text=subject_name)
        self.save_data()
    
    def change_assignment(self, row, col, assignment_name, deadline):
        self.data[row][col]["assignment"] = assignment_name
        self.data[row][col]["deadline"] = deadline

        remaining_days = self._calculate_remaining_days(deadline)
        text = f"{assignment_name}\n{deadline}"
        if remaining_days is not None and remaining_days < 2:
            self.labels[row][col].configure(text=text, fg="red")
        else:
            self.labels[row][col].configure(text=text, fg="green")

        self.save_data()
    
    def delete_data(self, row, col, subject_options_dialog=None, assignment_options_dialog=None):
        if row % 2 == 0:  
            self.data[row][col]["subject"] = ""
            self.labels[row][col].configure(text="")
        else:  
            self.data[row][col] = {"subject": "", "assignment": "", "deadline": ""}
            self.labels[row][col].configure(text="")
        if subject_options_dialog:
            subject_options_dialog.dialog.destroy()
        if assignment_options_dialog:
            assignment_options_dialog.dialog.destroy()
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
                    self.labels[row][col].configure(text=subject, fg="black")
                else:
                    self.labels[row][col].configure(text=assignment + "\n" + deadline)
                    remaining_days = self._calculate_remaining_days(deadline)
                    if remaining_days is not None and remaining_days < 2:
                        self.labels[row][col].configure(fg="red")
                    else:
                        self.labels[row][col].configure(fg="green")

        self.update_submitted_data()


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
    
    def update_assignment(self, row, col, assignment_name, deadline):
        self.data[row][col]["assignment"] = assignment_name
        self.data[row][col]["deadline"] = deadline

        remaining_days = self._calculate_remaining_days(deadline)

        self.save_data()

    def return_assignment_to_timetable(
        self, assignment_index, assignment_name, deadline, cell_row, cell_col
    ):
        self.submitted_data.pop(assignment_index)
        self.update_submitted_data()  
        self.data[cell_row][cell_col]["assignment"] = assignment_name
        self.data[cell_row][cell_col]["deadline"] = deadline

        remaining_days = self._calculate_remaining_days(deadline)
        text = f"{assignment_name}\n{deadline}"
        if remaining_days is not None and remaining_days < 2:
            self.labels[cell_row][cell_col].configure(text=text, fg="red")
        else:
            self.labels[cell_row][cell_col].configure(text=text, fg="green")

        self.save_data() 

    def update_submitted_data(self):
        self.submitted_data_label.delete(0, tk.END)
        for assignment in self.submitted_data:
            text = f"{assignment['assignment']} (期限: {assignment['deadline']})"
            self.submitted_data_label.insert(tk.END, text)


class InputClassControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def change_subject(self, row, col, subject_name):
        self.data[row][col]["subject"] = subject_name
        self.labels[row][col].configure(text=subject_name)
        self.save_data()


class ChangeOfClassControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def update_subject(self, row, col, class_name):
        self.data[row][col]["class"] = class_name
        self.save_data()


class DeleteClassControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def delete_data(self, row, col, subject_options_dialog=None, assignment_options_dialog=None):
        if row % 2 == 0:  
            self.data[row][col]["subject"] = ""
            self.labels[row][col].configure(text="")
        else:  
            self.data[row][col] = {"subject": "", "assignment": "", "deadline": ""}
            self.labels[row][col].configure(text="")
        if subject_options_dialog:
            subject_options_dialog.dialog.destroy()
        if assignment_options_dialog:
            assignment_options_dialog.dialog.destroy()
        self.save_data()


class InputAssignmentControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def change_assignment(self, row, col, assignment_name, deadline):
        self.data[row][col]["assignment"] = assignment_name
        self.data[row][col]["deadline"] = deadline

        remaining_days = self._calculate_remaining_days(deadline)
        text = f"{assignment_name}\n{deadline}"
        if remaining_days is not None and remaining_days < 2:
            self.labels[row][col].configure(text=text, fg="red")
        else:
            self.labels[row][col].configure(text=text, fg="green")

        self.save_data()


class ChangeOfAssignmentControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def update_assignment(self, row, col, assignment_name, deadline):
        self.data[row][col]["assignment"] = assignment_name
        self.data[row][col]["deadline"] = deadline

        remaining_days = self._calculate_remaining_days(deadline)

        self.save_data()    


class DeleteAssignmentControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def delete_data(self, row, col, subject_options_dialog=None, assignment_options_dialog=None):
        if row % 2 == 0:  
            self.data[row][col]["subject"] = ""
            self.labels[row][col].configure(text="")
        else:  
            self.data[row][col] = {"subject": "", "assignment": "", "deadline": ""}
            self.labels[row][col].configure(text="")
        if subject_options_dialog:
            subject_options_dialog.dialog.destroy()
        if assignment_options_dialog:
            assignment_options_dialog.dialog.destroy()
        self.save_data()


class MoveAssignmentControl:
    def __init__(self, timetable, cell_row, cell_col):
        self.timetable = timetable
        self.cell_row = cell_row
        self.cell_col = cell_col

    def move_assignment_to_submitted(self, row, col, assignment_options_dialog=None):
        assignment_name, deadline = self.data[row][col]["assignment"], self.data[row][col]["deadline"]
        if assignment_name and deadline:
            self.submitted_data.append(
                {"assignment": assignment_name, "deadline": deadline, "cell_row": row, "cell_col": col}
            )
            self.data[row][col]["assignment"] = ""
            self.data[row][col]["deadline"] = ""
            self.labels[row][col].configure(text="", fg="black")
            self.update_submitted_data()
            self.save_data()
        if assignment_options_dialog:
            assignment_options_dialog.destroy()

class ReturnAssignmentControl:
    def __init__(self, timetable, assignment_index, assignment_name, deadline, cell_row, cell_col):
        self.timetable = timetable
        self.assignment_index = assignment_index
        self.assignment_name = assignment_name
        self.deadline = deadline
        self.cell_row = cell_row
        self.cell_col = cell_col

    def return_assignment_to_timetable(
        self, assignment_index, assignment_name, deadline, cell_row, cell_col
    ):
        self.submitted_data.pop(assignment_index)
        self.update_submitted_data_label()  
        self.data[cell_row][cell_col]["assignment"] = assignment_name
        self.data[cell_row][cell_col]["deadline"] = deadline

        remaining_days = self._calculate_remaining_days(deadline)
        text = f"{assignment_name}\n{deadline}"
        if remaining_days is not None and remaining_days < 2:
            self.labels[cell_row][cell_col].configure(text=text, fg="red")
        else:
            self.labels[cell_row][cell_col].configure(text=text, fg="green")

        self.save_data() 


class Timetable:
    DAYS = ["月", "火", "水", "木", "金"]
    TIME_LIMITS = ["1", "", "2", "", "3", "", "4", "", "5", "", "6", ""]

    def __init__(self):
        self.data = [[{"subject": "", "assignment": "", "deadline": ""} for _ in range(5)] for _ in range(12)]
        self.submitted_list = []

    def save_data(self):
        with open("timetable_data.pkl", "wb") as f:
            pickle.dump(self.data, f)
        with open("submitted_data.pkl", "wb") as f:
            pickle.dump(self.submitted_list, f)


class Class:
    def __init__(self, name):
        self.name = name
    
    def change_subject(self, row, col, subject_name):
        self.data[row][col]["subject"] = subject_name
        self.labels[row][col].configure(text=subject_name)
        self.save_data()

    def update_subject(self, row, col, assignment_name, deadline):
        self.data[row][col]["assignment"] = assignment_name
        self.data[row][col]["deadline"] = deadline
        self.save_data()

    def delete_data(self, row, col, subject_options_dialog=None, assignment_options_dialog=None):
        if row % 2 == 0:  
            self.data[row][col]["subject"] = ""
            self.labels[row][col].configure(text="")
        else:  
            self.data[row][col] = {"subject": "", "assignment": "", "deadline": ""}
            self.labels[row][col].configure(text="")
        if subject_options_dialog:
            subject_options_dialog.dialog.destroy()
        if assignment_options_dialog:
            assignment_options_dialog.dialog.destroy()
        self.save_data()


class Assignment:
    def __init__(self, name, deadline):
        self.name = name
        self.deadline = deadline

    def change_assignment(self, row, col, assignment_name, deadline):
        self.data[row][col]["assignment"] = assignment_name
        self.data[row][col]["deadline"] = deadline

        remaining_days = self._calculate_remaining_days(deadline)
        text = f"{assignment_name}\n{deadline}"
        if remaining_days is not None and remaining_days < 2:
            self.labels[row][col].configure(text=text, fg="red")
        else:
            self.labels[row][col].configure(text=text, fg="green")

        self.save_data()

    def update_assignment(self, row, col, assignment_name, deadline):
        self.data[row][col]["assignment"] = assignment_name
        self.data[row][col]["deadline"] = deadline

        remaining_days = self._calculate_remaining_days(deadline)

        self.save_data()    

    def delete_data(self, row, col, subject_options_dialog=None, assignment_options_dialog=None):
        if row % 2 == 0:  
            self.data[row][col]["subject"] = ""
            self.labels[row][col].configure(text="")
        else:  
            self.data[row][col] = {"subject": "", "assignment": "", "deadline": ""}
            self.labels[row][col].configure(text="")
        if subject_options_dialog:
            subject_options_dialog.dialog.destroy()
        if assignment_options_dialog:
            assignment_options_dialog.dialog.destroy()
        self.save_data()

    def move_assignment_to_submitted(self, row, col, assignment_options_dialog=None):
        assignment_name, deadline = self.data[row][col]["assignment"], self.data[row][col]["deadline"]
        if assignment_name and deadline:
            self.submitted_data.append(
                {"assignment": assignment_name, "deadline": deadline, "cell_row": row, "cell_col": col}
            )
            self.data[row][col]["assignment"] = ""
            self.data[row][col]["deadline"] = ""
            self.labels[row][col].configure(text="", fg="black")
            self.update_submitted_data()
            self.save_data()
        if assignment_options_dialog:
            assignment_options_dialog.destroy()


class Submitted:
    def __init__(self, name, deadline):
        self.name = name
        self.deadline = deadline
    
    def delete_submitted_data(self):
        self.submitted_data.delete(0, tk.END)

    def edit_submit_data(self, row, col, assignment_options_dialog=None):
            self.data[row][col]["assignment"] = ""
            self.data[row][col]["deadline"] = ""
            self.labels[row][col].configure(text="", fg="black")
            self.update_submitted_data()
            self.save_data()



if __name__ == "__main__":
    root = tk.Tk()
    app = TimetableScreen(root)
    root.mainloop()
