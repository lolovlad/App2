from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.textinput import TextInput
from time import sleep
from sqlite3 import connect


class Database:
    def __init__(self):
        self.connection = connect('database.db')
        self.cursor = self.connection.cursor()

    def init_db(self):
        try:
            self.clear_table()
        except:
            pass
        self.create_table()
        full_names = [
            "Иванов Иван Иванович",
            "Петрова Мария Сергеевна",
            "Сидоров Николай Петрович",
            "Кузнецова Ольга Владимировна",
            "Соколов Михаил Александрович",
        ]
        for i in full_names:
            self.insert_record(i)

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                time_added DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def clear_table(self):
        self.cursor.execute("""
            DROP TABLE students
        """)

    def insert_record(self, name):
        self.cursor.execute("""
            INSERT INTO students (name) VALUES (?)
        """, (name,))
        self.connection.commit()

    def get_all_records(self):
        self.cursor.execute("""
            SELECT * FROM students
        """)
        return self.cursor.fetchall()

    def update_last_record(self, name):
        self.cursor.execute("""
            UPDATE students SET name = ?
            WHERE id = (SELECT MAX(id) FROM students)
        """, (name,))
        self.connection.commit()


class AddStudentScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create layout
        layout = BoxLayout(orientation='vertical')
        self.db = Database()

        self.label_name = Label(text="Имя:")
        self.input_name = TextInput()

        self.label_last_name = Label(text="Фамилия:")
        self.input_last_name = TextInput()

        self.label_patronymic = Label(text="Отчество:")
        self.input_patronymic = TextInput()

        # Create button to add student
        self.btn_add_student = Button(text="Добавить")

        # Add widgets to the layout
        layout.add_widget(self.label_name)
        layout.add_widget(self.input_name)
        layout.add_widget(self.label_last_name)
        layout.add_widget(self.input_last_name)
        layout.add_widget(self.label_patronymic)
        layout.add_widget(self.input_patronymic)
        layout.add_widget(self.btn_add_student)

        # Add layout to the screen
        self.add_widget(layout)

        # Bind button event
        self.btn_add_student.bind(on_press=self.on_add_student_pressed)

    def on_add_student_pressed(self, instance):
        name = self.input_name.text
        last_name = self.input_last_name.text
        patronymic = self.input_patronymic.text
        self.input_name.text = ''
        self.input_last_name.text = ''
        self.input_patronymic.text = ''
        self.db.insert_record(f"{last_name} {name} {patronymic}")
        self.manager.transition.direction = 'right'
        self.manager.current = 'main_screen'


class ScreenMain(Screen):
    def __init__ (self, **kwargs):
        super().__init__(**kwargs)

        self.db = Database()
        self.db.init_db()

        btn_show_data = Button(text="Показать данные")
        btn_add_record = Button(text="Добавить запись")
        btn_update_record = Button(text="Обновить последнюю запись")

        boxlayout = BoxLayout(orientation="vertical", spacing=5, padding=[10])

        boxlayout.add_widget(btn_show_data)
        boxlayout.add_widget(btn_add_record)
        boxlayout.add_widget(btn_update_record)

        btn_show_data.bind(on_press=self.on_show_data_pressed)
        btn_add_record.bind(on_press=self.on_add_record_pressed)
        btn_update_record.bind(on_press=self.on_update_record_pressed)

        self.add_widget(boxlayout)

    def on_show_data_pressed(self, instance):
        self.manager.get_screen('lenpasword').view_data()
        self.manager.transition.direction = 'left'
        self.manager.current = 'lenpasword'

    def on_add_record_pressed(self, instance):
        self.manager.transition.direction = 'left'
        self.manager.current = 'add_user'

    # Обработчик события нажатия кнопки "Обновить последнюю запись"
    def on_update_record_pressed(self, instance):
        # Замена ФИО в последней записи
        self.db.update_last_record("Иванов Иван Иванович")


class MyLabel(Label):
    def __init__(self, text="", **kwargs):
        super().__init__(text=text, **kwargs)
        self.padding = (10, 10)
        self.halign = 'left'
        self.font_size = '16sp'


class LenPasword(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        try:
            self.db = Database()
        except:
            pass

        self.boxlayout = BoxLayout(orientation="vertical", spacing=5, padding=[10])

        btn_menu = Button(text="Назад")
        btn_menu.bind(on_press=self._on_press_button_new_pasword)

        self.boxlayout.add_widget(btn_menu)
        self.add_widget(self.boxlayout)

    def _on_press_button_new_pasword(self, *args):
        self.manager.transition.direction = 'right'
        self.manager.current = 'main_screen'

    def removeMyLabel(self):
        rows = [i for i in self.boxlayout.children]

        for row1 in rows:
            if isinstance(row1, MyLabel):
                self.boxlayout.remove_widget(row1)

    def view_data(self):
        self.removeMyLabel()
        try:
            data = self.db.get_all_records()
        except:
            data = []

        for record in data:
            self.boxlayout.add_widget(
                MyLabel(text=f"{record[0]}\n{record[1]}\n{record[2]}"))



class PaswordingApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ScreenMain(name='main_screen'))
        sm.add_widget(LenPasword(name='lenpasword'))
        sm.add_widget(AddStudentScreen(name="add_user"))

        return sm

if __name__ == "__main__":
    PaswordingApp().run()