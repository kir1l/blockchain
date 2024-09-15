import flet
from flet import *

from wallet import Wallet

class WalletSendPage(Container):
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

       self.error_message = Text("", size=16, text_align=TextAlign.CENTER, color=flet.colors.RED)

       self.recipient_address = TextField(
            label="Recipient Address",
            width=400,
            border_color=flet.colors.WHITE
        )

       self.amount_input = TextField(
            label="Amount",
            width=400,
            border_color=flet.colors.WHITE
        )

       self.send_button = ElevatedButton(
            text="Send",
            on_click=self.send_transaction,
            height=50,
            width=200,
            bgcolor='#2A323C'
       )

       self.content = Container(
           content=Column(
               [
                   self.header,
                   self.error_message,
                   self.recipient_address,
                   self.amount_input,
                   self.send_button,
               ],
               alignment=MainAxisAlignment.CENTER,
               horizontal_alignment=CrossAxisAlignment.CENTER,
               spacing=20,
           ),
           margin=0,
           padding=padding.only(top=20, bottom=40, left=20, right=20),

           bgcolor="#191E24",
           border_radius=20,
           alignment=alignment.center,
       )

   def update_dynamic_info(self, wallet: Wallet):
       self.wallet = wallet

   def send_transaction(self, e):
       recipient = self.recipient_address.value
       amount = self.amount_input.value

       if len(recipient) != 34:
           self.error_message.value = "Invalid recipient address"
           self.error_message.update()
           return

       try:
           amount = int(amount)
       except ValueError:
           self.error_message.value = "Invalid amount"
           self.error_message.update()
           return

       if amount <= 0:
           self.error_message.value = "Amount must be greater than 0"
           self.error_message.update()
           return

       last_balance = self.wallet.get_balance()
       
       if amount > last_balance:
           self.error_message.value = "Insufficient balance"
           self.error_message.update()
           return

       if recipient == self.wallet.address:
           self.error_message.value = "You cannot send to yourself"
           self.error_message.update()
           return

       self.error_message.value = ""
       self.error_message.update()

       response = self.wallet.send_transaction(recipient=recipient, amount=amount)

       if response:
           self.error_message.value = "Transaction successful"
           self.error_message.color = flet.colors.GREEN
           self.error_message.update()
       else:
           self.error_message.value = "Transaction failed"
           self.error_message.update()
