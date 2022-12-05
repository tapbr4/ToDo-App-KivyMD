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
from datetime import datetime
from plyer import notification
from plyer import vibrator
from plyer import flash
import requests
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
    url = '' #Firebase URL
    auth_key = '' #Firebase Auth Key
    dialog = None
    path = ''

    #Botão voltar (Android) / ESC
    def on_pre_enter(self):
        self.ids.box.clear_widgets()
        self.path = MDApp.get_running_app().user_data_dir+'/'
        Window.bind(on_keyboard=self.voltar)
        #Firebase
        request = requests.get(self.url + '?auth=' + self.auth_key)
        JSON = request.json()
        for key in list(JSON.keys()):
            #Add widget
            self.ids.box.add_widget(Tarefa(text=key))

    def voltar(self, window, key, *args):
        if key == 27:
            MDApp.get_running_app().root.current = 'menu'
            return True

    def on_pre_leave(self):
        Window.unbind(on_keyboard=self.voltar)

    #Adicionar Tarefa
    def addWidget(self):
        texto = self.ids.texto.text
        if not (texto.isspace() or texto == '') and (len(texto) <= 20):
            #Add Widget
            self.ids.box.add_widget(Tarefa(text=texto))
            #Firebase
            JSON = {texto:{"date":datetime.today().strftime('%Y-%m-%d %H:%M:%S')}}
            JSON = json.dumps(JSON)
            to_database = json.loads(JSON)
            requests.patch(url=self.url, json=to_database)   
            #Clear text input
            self.ids.texto.text = ''
        elif (len(texto) > 20) and not (texto.isspace()):
            Todo.aviso(texto='Seu texto não pode ter mais que 20 caracteres.')
            self.ids.texto.text = ''          
        else:
            Todo.aviso(texto='Você precisa escrever alguma coisa!')
            self.ids.texto.text = ''  
    
    def delete(self, texto):
        #Firebase
        JSON = f'{texto}/date'
        requests.delete(url=self.url[:-5]+JSON+".json")
            


class Tarefa(MDBoxLayout):
    dialog = None
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

    def delete(self, *args):
        app = MDApp.get_running_app()
        #Firebase
        texto = self.ids.label.text
        Tarefas.delete(Tarefas, texto)
        #Remove Widget
        app.root.get_screen('tarefas').ids.box.remove_widget(self)
        self.dialog.dismiss()


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