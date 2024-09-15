import flet

from views.open_page import OpenPage
from views.import_page import ImportWalletPage
from views.create_page import CreateWalletPage
from views.main_wallet_page import MainWalletPage
from views.wallet_send import WalletSendPage
from views.wallet_receive import WalletReceivePage

from wallet import Wallet

class MainApp:
    def __init__(self, page: flet.Page):
        self.page = page
        
        # Init the pages
        self.open_page = OpenPage(self.page)
        self.import_page = ImportWalletPage(self.page)
        self.create_page = CreateWalletPage(self.page)
        self.main_wallet_page = MainWalletPage(self.page)
        self.wallet_send_page = WalletSendPage(self.page)
        self.wallet_receive_page = WalletReceivePage(self.page)

        # Main page settings
        self.window_width = 500
        self.window_height = 700
        self.theme_mode = flet.ThemeMode.DARK
        page.window_width = self.window_width
        page.window_height = self.window_height
        page.vertical_alignment = flet.MainAxisAlignment.CENTER
        page.horizontal_alignment = flet.CrossAxisAlignment.CENTER
        page.theme_mode = self.theme_mode
        page.window_resizable = False
        page.window_title = "Bitplace Wallet"

        self.helper()

    def helper(self):
        self.page.on_route_change = self.on_route_change

        wallet = Wallet.load_wallet_local_data()

        if wallet:
            self.main_wallet_page.update_dynamic_info(wallet=wallet)
            self.page.go('/wallet', wallet)
        else:
            self.page.go('/')

    def on_route_change(self, route):
        route_page = {
            '/': self.open_page,
            '/importWallet': self.import_page,
            '/createWallet': self.create_page,
            '/wallet': self.main_wallet_page,
            '/wallet/send': self.wallet_send_page,
            '/wallet/receive': self.wallet_receive_page,
        }.get(self.page.route, self.open_page)

        if self.page.route == "/wallet" or self.page.route == "/wallet/send":
           wallet = Wallet.load_wallet_local_data()
           if wallet:
                 self.wallet_send_page.update_dynamic_info(wallet)
                 self.main_wallet_page.update_dynamic_info(wallet)

        self.page.views.clear()
        self.page.views.append(
            flet.View(
                route,
                [route_page] 
            )
        )
        self.page.update()

def main(page: flet.Page):
    MainApp(page)

if __name__ == '__main__':
    flet.app(target=main)
