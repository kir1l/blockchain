import flet
from flet import *
import pyperclip
from wallet import Wallet

class CreateWalletPage(Container):
    def __init__(self, page: flet.Page):
        super().__init__()
        self.page = page
        self.init_content()

    def init_content(self):
        header = Row(
            [
                Container(
                    content=Row([
                        Text("Bitplace Wallet", size=24),
                        Image(src="core/logo.png", width=30, height=30, fit=ImageFit.CONTAIN),
                    ])
                ),
                ElevatedButton(
                    icon=flet.icons.ARROW_BACK,
                    text="Back",
                    on_click=lambda _: self.page.go("/")
                )
            ],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            expand=True
        )

        self.wallet = None
        self.wallet_info = Column(visible=False)

        self.create_wallet_button = Container(
            content=ElevatedButton(
                text="Create Wallet",
                height=50,
                width=200,
                on_click=self.create_wallet
            ),
            padding=flet.padding.only(top=120)
        )

        content = Column(
            [
                header,
                Container(
                    content=self.create_wallet_button,
                    padding=flet.padding.only(top=50)
                ),
                self.wallet_info
            ],
            expand=True,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=15
        )

        self.content = content
        self.padding = 20 

        self.page.padding = 0
        self.page.update()

    def create_wallet(self, _):
        try:
            self.wallet = Wallet.create_wallet()

            wallet_address = Container(
                   content=Text(
                   self.wallet.address,
                   style=TextStyle(weight="bold"),
                   text_align="center",
                   no_wrap=True,
                   overflow="ellipsis",
                   size=18,
                ),
                on_click=lambda e: self.copy_with_alert(self.wallet.address, "Wallet address copied!"),
                border=border.only(bottom=border.BorderSide(1, colors.WHITE)),
                padding=padding.only(bottom=3),
             )

            seed_phrase_words = [
                Container(
                    content=Text(word, size=18, text_align="center"),
                    border=border.all(1, colors.GREY_400),
                    border_radius=5,
                    padding=5,
                    on_click=lambda e: self.copy_with_alert(self.wallet.seed_phrase, "Seed phrase copied!"),
                )
                for word in self.wallet.seed_phrase.split()
            ]

            seed_phrase_container = Container(
                content=Row(seed_phrase_words, wrap=True, alignment=MainAxisAlignment.CENTER),
                margin=10
            )

            go_to_wallet_button = Container(
                content=ElevatedButton(
                    text="Go to Wallet",
                    on_click=self.go_to_wallet,
                    height=50,
                    width=200
                ),
                margin=10,
                expand=True,
                padding=padding.only(top=20),
                alignment=alignment.center
            )

            self.wallet_info.controls = [
                Text("New wallet has been created!", size=22, text_align="center"),
                Container(padding=flet.padding.only(top=30)),
                Text("Your Wallet Address:", size=16, text_align="center"),
                wallet_address,
                Container(padding=flet.padding.only(top=30)),
                Text("Seed Phrase (Keep this safe!):", size=16, text_align="center"),
                seed_phrase_container,
                go_to_wallet_button
            ]
            self.create_wallet_button.visible = False
            self.wallet_info.visible = True

            self.page.update()
        except Exception as e:
            print(f"Failed to create wallet: {e}")

    def copy_with_alert(self, text, alert_message):
        pyperclip.copy(text)
        self.page.snack_bar = SnackBar(content=Text(alert_message))
        self.page.snack_bar.open = True
        self.page.update()

    def go_to_wallet(self, e):
       self.wallet.save_wallet_local_data()
       self.page.go("/wallet")
