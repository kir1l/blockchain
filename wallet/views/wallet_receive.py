import flet
from flet import *

from wallet import Wallet

class WalletReceivePage(Container):
   def __init__(self, page: flet.Page):
       super().__init__()
       self.page = page
       self.wallet = None
       self.init_content()

   def init_content(self):
       self.header = Container(
           content=Row(
               [
                   IconButton(
                       icon=flet.icons.ARROW_BACK,
                       on_click=lambda _: self.page.go("/wallet")
                   ),
                   Row([
                           Text("Bitplace Wallet", size=24),
                           Image(src="core/logo.png", width=30, height=30, fit=ImageFit.CONTAIN),
                   ])
               ],
               alignment=MainAxisAlignment.SPACE_BETWEEN,
               expand=True,
           ),
           bgcolor="#191E24",
           margin=0,
           padding=0
       )
       self.address = Container(
         content=Text('Loading', size=26)
       )
       
       self.last_transactions = Container(
         content=Text('Loading', size=26)
       )