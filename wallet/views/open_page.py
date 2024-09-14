import flet
from flet import Container, Text, Column, Row, ElevatedButton, Image, ImageFit, MainAxisAlignment, CrossAxisAlignment, colors
from wallet import Wallet

class OpenPage(Container):
    def __init__(self, page: flet.Page):
        super().__init__()
        self.page = page
        self.init_content()

    def init_content(self):
        header = Row(
            [
                Text("Bitplace Wallet", size=24),
                Image(src="core/logo.png", width=30, height=30, fit=ImageFit.CONTAIN)
            ],
            alignment=MainAxisAlignment.START
        )

        buttons = Row(
           [
                 ElevatedButton(text="Import Wallet", width=150, height=50, on_click=lambda _: self.page.go("/importWallet")),
                 ElevatedButton(text="Create Wallet", width=150, height=50, on_click=lambda _: self.page.go("/createWallet"))
           ],
           alignment=MainAxisAlignment.CENTER,
           spacing=23
        )

        heading_text = Text(
           "Welcome to Bitplace Wallet! Best place to store your crypto assets on Bitplace Blockchain.",
           size=20,
           text_align="center"
        )

        content = Column(
            [
                header,
                Container(
                    content=Column([
                        heading_text,
                        Container(padding=flet.padding.only(top=30)),
                        buttons
                    ]),
                    padding=flet.padding.only(top=130)
                )
            ],
            expand=True,
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=15
        )

        self.content = content
        self.padding = 20

        self.page.padding = 0
        self.page.update()