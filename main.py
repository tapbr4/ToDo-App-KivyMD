
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.utils import get_color_from_hex
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivy.core.window import Window
from kivy.utils import platform
from kivymd.app import MDApp
from kivy.clock import Clock
from plyer import notification
from plyer import vibrator
from plyer import flash
import json
import re


class Gerenciador(MDScreenManager):
    pass


class Menu(MDScreen):
    pass


class Login(MDScreen):

    def logar(self):
        email = self.ids.user.text
        password = self.ids.password.text

        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if (not EMAIL_REGEX.match(email)) and (email != '' and password != ''):
            Todo.aviso(texto='Insira um e-mail válido!')
        else:
            if(email == 'teste@teste.com') and (password == '12345'):
                self.parent.current = "menu"
            else:
                if email != '' and password != '':
                    Todo.aviso(texto='Senha incorreta ou Conta inexistente!')

        if email == '' or password == '':
            Todo.aviso(texto='Há um campo vazio no formulário!')


class Tarefas(MDScreen):
    dialog = None
    tarefas = []
    path = ''

    #Botão voltar (Android) / ESC
    def on_pre_enter(self):
        self.ids.box.clear_widgets()
        self.path = MDApp.get_running_app().user_data_dir+'/'
        self.loadData()
        Window.bind(on_keyboard=self.voltar)
        for tarefa in self.tarefas:
            self.ids.box.add_widget(Tarefa(text=tarefa))

    def voltar(self, window, key, *args):
        if key == 27:
            MDApp.get_running_app().root.current = 'menu'
            return True

    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar)
    
    def saveData(self, *args):
        with open(self.path+'data.json', 'w') as data:
            json.dump(self.tarefas,data)

    def loadData(self, *args):
        try:
            with open(self.path+'data.json', 'r') as data:
                self.tarefas = json.load(data)
                Tarefa.loadData(self=Tarefa)
        except FileNotFoundError:
            pass

    #Adicionar Tarefa
    def addWidget(self):
        texto = self.ids.texto.text
        if not (texto.isspace() or texto == '') and (len(texto) <= 20):
            self.ids.box.add_widget(Tarefa(text=texto))
            self.ids.texto.text = ''
            self.tarefas.append(texto)
            self.saveData()
            Tarefa.loadData(self=Tarefa)      
        elif (len(texto) > 20) and not (texto.isspace()):
            Todo.aviso(texto='Seu texto não pode ter mais que 20 caracteres.')
            self.ids.texto.text = ''          
        else:
            Todo.aviso(texto='Você precisa escrever alguma coisa!')
            self.ids.texto.text = ''         


class Tarefa(MDBoxLayout):
    dialog = None
    tarefas = []
    path = ''

    #Gerar tarefa
    def __init__(self, text='', **kwargs):
        super().__init__(**kwargs)
        self.ids.label.text = text
    
    def show_alert_dialog(self):
        if not self.dialog:
            self.dialog = MDDialog(
                text="Excluir Tarefa?",
                buttons=[
                    MDFlatButton(
                        text="CANCELAR",
                        theme_text_color="Custom",
                        on_release=lambda _: self.dialog.dismiss()),
                    MDRaisedButton(
                        text="DELETAR",
                        theme_text_color="Custom",
                        on_release=self.delete),],)
        self.dialog.open()

    def saveData(self, *args):
        self.path = MDApp.get_running_app().user_data_dir+'/'
        with open(self.path+'data.json', 'w') as data:
            json.dump(self.tarefas,data)

    def loadData(self, *args):
        self.path = MDApp.get_running_app().user_data_dir+'/'
        try:
            with open(self.path+'data.json', 'r') as data:
                self.tarefas = json.load(data)
        except FileNotFoundError:
            pass

    def delete(self, *args):
        app = MDApp.get_running_app()
        app.root.get_screen('tarefas').ids.box.remove_widget(self)
        self.dialog.dismiss()
        self.tarefas.remove(self.ids.label.text)
        self.saveData()
        

class Ferramentas(MDScreen):
    flashlight_status = 0

    def vibrator_on(self):
        app = MDApp.get_running_app()
        self.ids.vibratebutton.icon = 'vibrate'
        self.ids.vibratebutton.icon_color = app.theme_cls.primary_color
        vibrator.vibrate(1)
        Clock.schedule_once(self.vibrator_off, 1)
        
    def vibrator_off(self, *args):
        self.ids.vibratebutton.icon = 'vibrate-off'
        self.ids.vibratebutton.icon_color = get_color_from_hex('#696969')

    def send_notification(self):
        texto = self.ids.texto.text
        if not (texto.isspace() or texto == '') and (len(texto) <= 50):
            notification.notify(title='Notificação', 
                                message='Você escreveu: '+texto, 
                                app_name='ToDo App',
                                timeout=10)
                                #app_icon, ticker
        elif (len(texto) > 20) and not (texto.isspace()):
            Todo.aviso(texto='Seu texto não pode ter mais que 50 caracteres.')
            self.ids.texto.text = ''          
        else:
            Todo.aviso(texto='Você precisa escrever alguma coisa!')
            self.ids.texto.text = '' 

    def flashlight(self):
        app = MDApp.get_running_app()
        self.flashlight_status += 1
        if self.flashlight_status == 1:
            self.ids.flashbutton.icon = 'flashlight'
            self.ids.flashbutton.icon_color = app.theme_cls.primary_color
            flash.on()
        elif self.flashlight_status > 1:
            self.flashlight_status = 0
            self.ids.flashbutton.icon = 'flashlight-off'
            self.ids.flashbutton.icon_color = get_color_from_hex('#696969')
            flash.off()
            flash.release()

    #Botão voltar (Android) / ESC
    def on_pre_enter(self):
        Window.bind(on_keyboard=self.voltar)

    def voltar(self, window, key, *args):
        if key == 27:
            MDApp.get_running_app().root.current = 'menu'
            return True


class Todo(MDApp):
    def build(self):
        self.theme_cls.theme_style_switch_animation = True
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Dark"

        try:
            if platform == "android":
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.CAMERA, 
                                    Permission.READ_EXTERNAL_STORAGE, 
                                    Permission.WRITE_EXTERNAL_STORAGE,
                                    Permission.VIBRATE])
        except Exception as e:
            print(e)

        return Gerenciador()

    def switch_theme_style(self):
        self.theme_cls.theme_style = (
            "Dark" if self.theme_cls.theme_style == "Light" else "Light"
        )

    def aviso(texto):
        dialog = None
        if not dialog:
            dialog = MDDialog(
                text=texto,
                    buttons=[
                        MDFlatButton(
                            text="OK",
                            theme_text_color="Custom",
                            on_release=lambda _: dialog.dismiss())])
        dialog.open()

    def set_screen(self, screen_name):
        self.root.current = screen_name


Todo().run()