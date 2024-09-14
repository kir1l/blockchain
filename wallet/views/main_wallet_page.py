import flet
from flet import *

from wallet import Wallet
import threading
import time


class MainWalletPage(Container):
   def __init__(self, page: flet.Page):
       super().__init__()
       self.page = page
       self.wallet = None
       self.update_thread = None
       self.init_content()

   def init_content(self):
       self.header = Container(
           content=Row(
               [
                   IconButton(
                       icon=flet.icons.NOTIFICATIONS,
                       on_click=lambda _: self.page.go("/")
                   ),
                   Row([
                           Text("Bitplace Wallet", size=24),
                           Image(src="core/logo.png", width=30, height=30, fit=ImageFit.CONTAIN),
                   ]),
                   PopupMenuButton(
                       icon=flet.icons.SETTINGS,
                       items=[
                           PopupMenuItem(text="Log out", on_click=self.logout)
                       ]
                   )
               ],
               alignment=MainAxisAlignment.SPACE_BETWEEN,
               expand=True,
           ),
           bgcolor="#191E24",
           border_radius=border_radius.only(top_left=10, top_right=10),
           margin=0,
           padding=10
       )

       self.total_balance = Text("Loading", size=28, text_align=TextAlign.CENTER)
       self.wallet_name = Text(f"Main Wallet", size=16, text_align=TextAlign.CENTER, color=flet.colors.GREY)

       self.main_box = Container(
           content=Column(
               [
                   Column(
                       [
                           self.total_balance,
                           # Strip last 5 digits of address
                           self.wallet_name,
                       ],
                       expand=True,
                       alignment=MainAxisAlignment.CENTER,
                       horizontal_alignment=CrossAxisAlignment.CENTER
                   ),
                   Container(
                        border=border.only(bottom=border.BorderSide(1, "#2A323C")), 
                        expand=True,
                        margin=margin.only(right=40, left=40, top=30),
                     ),
                   Container(
                       content=Row(
                           [
                               Column(
                                   [
                                       IconButton(icons.SEND_ROUNDED, on_click=lambda _: self.page.go("/wallet/send"), icon_size=26),
                                       Text("Send")
                                   ],
                                   spacing=0,
                                   alignment=MainAxisAlignment.CENTER,
                                   horizontal_alignment=CrossAxisAlignment.CENTER
                               ),
                               Column(
                                   [
                                       IconButton(icons.DOWNLOAD_ROUNDED, on_click=lambda _: self.page.go("/receive"), icon_size=26),
                                       Text("Receive")
                                   ],
                                   spacing=0,
                                   alignment=MainAxisAlignment.CENTER,
                                   horizontal_alignment=CrossAxisAlignment.CENTER
                               )
                           ],
                           alignment=MainAxisAlignment.SPACE_EVENLY
                       ),
                       padding=padding.only(top=30)
                   )
               ],
               expand=True,
               alignment=MainAxisAlignment.CENTER,
               horizontal_alignment=CrossAxisAlignment.CENTER,
               spacing=0
           ),
           bgcolor="#191E24",
           border_radius=border_radius.only(bottom_left=10, bottom_right=10),
           padding=padding.symmetric(vertical=30),
           margin=0
       )

       self.bitplace_balance = Text("Loading", size=16, text_align=TextAlign.CENTER)

       self.funds_box = Container(
           content=Column(
               [
                   Container(
                       content=Row(
                           [  
                               Container(content=Image(src="core/logo.png", width=40, height=40, fit=ImageFit.CONTAIN)),
                               Container(content=
                                   Column(
                                       [
                                           Text("Bitplace coin", size=14, text_align=TextAlign.CENTER),
                                           self.bitplace_balance
                                       ],
                                       expand=True,
                                       spacing=0
                                   )
                               ),
                           ]
                       ),
                       padding=10,
                       border=border.only(bottom=border.BorderSide(1, "#2A323C"), top=border.BorderSide(1, "#2A323C")),
                   )
               ]
           ),
       ) 

       self.content = Column(
           [
               self.header,
               self.main_box,
               Container(
                   content=Text("Assets", size=20),
                   padding=padding.only(top=10, bottom=10),
                   expand=True,
               ),
               self.funds_box
           ],
           expand=True,
           alignment=MainAxisAlignment.START,
           horizontal_alignment=CrossAxisAlignment.CENTER,
           spacing=0,
       )

   def update_dynamic_info(self, wallet: Wallet):
       self.wallet = wallet

       self.total_balance.value = f"${self.wallet.get_balance()}"
       self.bitplace_balance.value = f"${self.wallet.get_balance()}"
       self.wallet_name.value =  f'Main Wallet ...{self.wallet.address[-5:]}'

       if not self.update_thread or not self.update_thread.is_alive():
            self.update_thread = threading.Thread(target=self.update_balance_periodically)
            self.update_thread.daemon = True
            self.update_thread.start()

   def update_balance_periodically(self):
        while self.wallet:
            if self.wallet:
                new_balance = self.wallet.get_balance()
                self.total_balance.value = f"${new_balance}"
                self.bitplace_balance.value = f"${new_balance}"
                self.page.update()
            time.sleep(10)  # Обновление каждые 10 секунд

   def logout(self, e):
       self.wallet.delete_wallet_local_data()
       self.page.go("/")