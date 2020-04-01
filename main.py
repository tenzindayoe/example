

from kivymd.app import MDApp
from kivymd.uix.taptargetview import MDTapTargetView

from kivy.properties import ObjectProperty

from kivy.garden.mapview import MapView ,MapMarker
from kivy.uix.screenmanager import Screen,ScreenManager,SlideTransition
from kivymd.uix.snackbar import Snackbar


from kivy.uix.boxlayout import BoxLayout
import sqlite3
import socket
from kivy.clock import Clock
from kivymd.uix.dialog import MDInputDialog
from urllib import parse
from kivy.network.urlrequest import UrlRequest

from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivy.properties import StringProperty
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.theming import ThemableBehavior
from kivymd.uix.list import MDList
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from gpsblinker import GpsBlinker
host = ''  # client ip
port = 12345
server = ('3.21.122.235', 12345)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
from gpshelper import GpsHelper
rtr_count = 0

#Connect to the local account database
account_db = sqlite3.connect("account.db")

ac_db_cur = account_db.cursor()

ac_db_cur.execute("SELECT * FROM accounts")
def remove():
    ac_db_cur.execute("DELETE FROM accounts ")
    ac_db_cur.execute("DELETE FROM avatar")
    account_db.commit()

usr_ac_cred = ac_db_cur.fetchall()
print(usr_ac_cred)
logged_in = None

if len(usr_ac_cred) == 0:
    logged_in = False
elif len(usr_ac_cred) != 0:

    usr_ac_cred.append("ch_acc_cred")
    print(usr_ac_cred)
    # connect to server for verification
    s.sendto(str(usr_ac_cred).encode("utf-8"), server)

    # DATA FROM SERVER
    data, addr = s.recvfrom(1024)
    data = data.decode('utf-8')
    data = eval(data)

    if data[0] == "verified" or data[0] == "error_lia":
        if data[0] == "verified":
            logged_in = True
            rtr_count += 3

        elif data[0] == "error_lia":
            logged_in = False
    print(logged_in)
class ScreenOne(Screen):
    pass
class ScreenTwo(Screen):
    pass
class ScreenThree(Screen):
    pass

class SearchPopupMenu(MDInputDialog):
    title = "Search by Address"
    text_button_ok = "Search"
    def __init__(self):
        super().__init__()
        self.size_hint = [.8,.3]
        self.opacity = 1
        self.events_callback = self.callback
    def callback(self,*args):
        address = self.text_field.text
        self.geocode_get_lat_lon(address)
    def geocode_get_lat_lon(self,address):
        address = parse.quote(address)
        url = "https://geocoder.api.here.com/search/6.2/geocode.json?languages=en-US&maxresults=4&searchtext=%s&app_id=%s&app_code=%s"%(address,"ZtzdZR3JSRAx1UnXce6L","XUq5cGi9z4S-7jlnDhf_7g")
        UrlRequest(url,on_success=self.success,on_failure=self.failure,on_error=self.error)
    def success(self,urlrequest,result):
        print("success")
        print(result)
    def failure(self,urlrequest,result):
        print("Failure")
        print(result)
    def error(self,urlrequest,result):
        print("Error")
        print(result)



class Main(MapView):
    getting_markers_timer = None


    def start_getting_markers_in_fov(self):
        self.map_source = "osm"
        #after one second get markers in fov\
        try :

            self.getting_markers_timer.cancel()
        except:
            pass
        self.getting_markers_timer = Clock.schedule_once(self.get_markers_in_fov,1)

    def get_markers_in_fov(self,*args):


        unp_bound = self.get_bbox()
        bound = []
        bound.append([unp_bound[1],unp_bound[3]])
        bound.append([unp_bound[0],unp_bound[2]])

        s.sendto(str(bound).encode('utf-8'), server)
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        if data != "error_lia" or data != "verified":
            data = eval(data)
            for obj in data:


                self.add_marker(MapMarker(lat=obj[1],lon = obj[0]))
            print("transaction successful")

class MyWidget(Widget):
    def __init__(self, **args):
        super(MyWidget, self).__init__(**args)
        self.texture = Texture.create(size=(2, 2), colorfmt='rgba')

        p1_color = [255, 96, 27, 255]
        p2_color = [255, 0, 133, 255]
        p3_color = [206, 255, 0, 255]
        p4_color = [232, 202, 0, 255]
        p1_color = [0, 171, 146, 255]
        p2_color = [0, 174, 109, 255]
        p3_color = [0, 138, 175, 255]
        p4_color = [15, 154, 174, 255]

        p = p1_color + p2_color + p3_color + p4_color
        buf = bytes(p)
        self.texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=self.size, texture=self.texture)

        self.bind(size=self.update_rect)
        self.bind(pos=self.update_rect)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

#load map
settings_db = sqlite3.connect("Settings.db")
cur = settings_db.cursor()

cur.execute("select * from settings")
data_un= cur.fetchall()
print(data_un)

           
                    
                


class DrawerList(ThemableBehavior, MDList):
    def set_color_item(self, instance_item):
        '''Called when tap on a menu item.'''

        # Set the color of the icon and text for the menu item.
        for item in self.children:
            if item.text_color == self.theme_cls.primary_color:
                item.text_color = self.theme_cls.text_color
                break
        instance_item.text_color = self.theme_cls.primary_color

class Settings_screen_list(OneLineAvatarIconListItem):
    icon = StringProperty("android")
class Right_switch(IRightBodyTouch,MDSwitch):
    pass

class Manager(ScreenManager):
    Home = ObjectProperty(None)
    Settings = ObjectProperty(None)

class MainApp(MDApp):
    data = {
        "help-circle-outline" : "Help",
        "mapbox" : "Add Trashcan",
        "settings" : "settings"
    }
    myscreen = ObjectProperty()
    search_menu= None



    def on_start(self):

        try:
            self.root.ids.avatar_usr.source = ac_db_cur.execute("SELECT * FROM avatar").fetchall()[0][0]
            self.root.ids.avatar_usr_2.source = ac_db_cur.execute("SELECT * FROM avatar").fetchall()[0][0]
            self.root.ids.uad_username.text = usr_ac_cred[0][1]
            self.root.ids.uad_email.text = usr_ac_cred[0][0]
            self.root.ids.nav_username.text = usr_ac_cred[0][1]
            self.root.ids.nav_email.text = usr_ac_cred[0][0]
            #initialize gps

        except:
            pass

    def build(self):

        #Accessing settings database
        cur.execute("SELECT mode from settings where attribute='darkmode' ")
        GpsHelper().run()
        #App theme and UI color schemes
        darkmode_opt_list = cur.fetchall()
        darkmode_opt = darkmode_opt_list[0][0]
        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.primary_hue = "800"
        self.theme_cls.accent_palette  = "Gray"
        self.theme_cls.accent_hue = "50"
        self.search_menu = SearchPopupMenu()

        self.tap_target_view = MDTapTargetView(
            widget=self.root.ids.button,
            title_text="Click here to locate you.",
            description_text="Make sure we are right over you",
            widget_position="left_bottom",
        )
        if darkmode_opt == "on":
            print("dark mode on")
            self.theme_cls.theme_style = "Dark"
            self.root.ids.darkmode_switch.active= True
        else:
            print("light mode on")
            self.theme_cls.theme_style = "Light"
            self.root.ids.darkmode_switch.active = False


        if logged_in == True:
            self.root.ids.manager.current = "Home"
            self.root.ids.ecomap.add_marker(MapMarker(lat=60, lon=30))
            myloc = MapMarker(lat=30.3433, lon=77.8839)
            self.root.ids.ecomap.add_marker(myloc)

            def repos(button):
                self.root.ids.ecomap.center_on(31.901303405681098, 76.5568)
                self.root.ids.ecomap.zoom = 18

            self.tap_target_view.bind(on_close=repos)

            def drop_marker_db(button):
                pass
                # temp_marker = MapMarker(lat=val[0], lon=val[1])
                # screen.ids.ecomap.add_marker(temp_marker)

            try:
                self.start_anim.cancel()
            except:
                pass
            self.start_anim = Clock.schedule_once(self.start_tp_anim, 3.5)



        elif logged_in == False:
            self.root.ids.parent_manager.current = "account_setup"


    def start_app(self):

        self.root.ids.parent_manager.current = "parent"
        self.root.ids.manager.current = "Home"
        usr_ac_cred = ac_db_cur.execute("SELECT * FROM accounts").fetchall()
        self.root.ids.uad_username.text = usr_ac_cred[0][1]
        self.root.ids.uad_email.text = usr_ac_cred[0][0]
        self.root.ids.nav_username.text = usr_ac_cred[0][1]
        self.root.ids.nav_email.text = usr_ac_cred[0][0]


    def start_tp_anim(self,*args):
        self.tap_target_start()
    def init_dark_mode(self,select,value):
        if value:
            self.theme_cls.theme_style = "Dark"
            cur.execute("UPDATE settings SET mode='on' WHERE attribute = 'darkmode'")
            settings_db.commit()
        else:
            self.theme_cls.theme_style = "Light"
            cur.execute("UPDATE settings SET mode='off' WHERE attribute = 'darkmode'")
            settings_db.commit()
    def tap_target_start(self):
        if self.tap_target_view.state == "close":
            self.tap_target_view.start()
        else:
            self.tap_target_view.stop()
    def callback(self,instance):
        if instance.icon == "settings":
            self.root.ids.manager.transition= SlideTransition()
            self.root.ids.manager.current = "Settings"
        elif instance.icon == "mapbox":
            self.register_trashcan()
        elif instance.icon == "help-circle-outline":
            pass
    def open_account(self):
        self.root.ids.parent_manager.current="User_account_details"

    def open_home(self):
        self.root.ids.manager.current="Home"
    def sign_up(self):
        username = self.root.ids.name_field.text
        email = self.root.ids.email_field.text
        password = self.root.ids.password_field.text
        Acc_list = ["acc", username, email, password]
        Acc_list = str(Acc_list)

        s.sendto(Acc_list.encode("utf-8"),server)
        response,response_addr = s.recvfrom(1024)

        response = response.decode("utf-8")
        if response == "ACCOUNT CREATED":
            sql_script = "INSERT INTO accounts VALUES('" + email + "', '" + username + "' , '" + password + "')"
            ac_db_cur.execute(sql_script)
            account_db.commit()
            self.root.ids.parent_manager.current = "profile_picture_opt"
            self.root.ids.uad_username.text = username
            self.root.ids.uad_email.text = email
            self.root.ids.nav_username.text = username
            self.root.ids.nav_email.text = email

        #register this account to server database


        #register this account credentials to localhost database

    def go_to_login(self):
        self.root.ids.parent_manager.current = "login_screen"

    def login(self):
        if self.root.ids.login_email_field == "" or self.root.ids.login_pw_field =="" :
            print("Empty fields detected")
        else:
            cred_cont = [(self.root.ids.login_email_field.text,"",self.root.ids.login_pw_field.text),"ch_acc_cred"]
            s.sendto(str(cred_cont).encode("utf-8"),server)
            response, response_addr = s.recvfrom(1024)
            response = response.decode("utf-8")
            if response == "error_lia":
                pass
            else:
                response = eval(response)
                if response[0]=="verified":
                    sql_scr1 = "DELETE FROM accounts"
                    sql_scr2 = "INSERT INTO accounts VALUES('"+self.root.ids.login_email_field.text+"', '"+response[1]+"' , '"+self.root.ids.login_pw_field.text+"')"
                    ac_db_cur.execute(sql_scr1)
                    ac_db_cur.execute(sql_scr2)
                    account_db.commit()
                    global logged_in
                    logged_in = True
                    self.root.ids.parent_manager.current = "profile_picture_opt"

    def confirm_av(self):
        usr_av = None
        selected = None

        for avatar in [self.root.ids.m1,self.root.ids.m2,self.root.ids.m3,self.root.ids.m4,self.root.ids.m5,self.root.ids.m6,self.root.ids.m7,self.root.ids.w1,self.root.ids.w2,self.root.ids.w3,self.root.ids.w4,self.root.ids.w5,self.root.ids.w6,self.root.ids.w7]:

            if avatar.size == [130,130]:

                selected = True
                break
        if selected == True:
            ac_db_cur.execute("DELETE FROM avatar")
            ac_db_cur.execute("INSERT INTO avatar VALUES('"+avatar.icon+"')")
            account_db.commit()
            self.start_app()
            av = ac_db_cur.execute("SELECT * FROM avatar").fetchall()[0][0]

            self.root.ids.avatar_usr.source = av
            self.root.ids.avatar_usr_2.source = av
        else :
            pass
    def register_trashcan(self):
        lat = self.root.ids.blinker.lat
        lon = self.root.ids.blinker.lon
        list = ["tr_reg",[lat,lon]]
        s.sendto(str(list).encode("utf-8"),server)
        self.snackbar = Snackbar(text="Trashcan added.Will be shown soon!")
        self.snackbar.show()






MainApp().run()