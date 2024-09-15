import flet
from flet import *
from wallet import Wallet

class ImportWalletPage(Container):
    def __init__(self, page: flet.Page):
        super().__init__()
        self.page = page
        self.init_content()

    def init_content(self):
        self.header = Row(
            [
                Text("Import Wallet", size=24),
                ElevatedButton(
                    icon=flet.icons.ARROW_BACK,
                    text="Back",
                    on_click=lambda _: self.page.go("/")
                )
            ],
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            expand=True
        )

        self.seed_phrase_input = TextField(
            label="Seed Phrase",
            multiline=True,
            max_lines=3,
            width=400,
            border_color=flet.colors.WHITE
        )

        self.error_message = Text(
            "",
            color=flet.colors.RED
        )

        self.import_button = ElevatedButton(
            text="Import Wallet",
            on_click=self.import_wallet
        )

        content = Column(
            [
                self.header,
                Container(padding=flet.padding.only(top=50)),
                Text("Enter your seed phrase", size=18),
                self.error_message,
                self.seed_phrase_input,
                self.import_button
            ],
            expand=True,
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            spacing=20
        )

        self.content = content
        self.padding = 20

    def import_wallet(self, e):
        seed_phrase = self.seed_phrase_input.value
        
        if seed_phrase:
            try:
                wallet = Wallet.from_seed_phrase(seed_phrase)
                wallet.save_wallet_local_data()
                self.page.go("/wallet")
            except Exception as ex:
                self.error_message.value = str(ex)
                self.page.update()
        else:
            self.error_message.value = "Please enter seed phrase"
            self.page.update()
