from core.actions.screen import wait, drag, exist, exist_click, log_msg, open_external_url, launch_game
from core.system.config import Config

class LinkNavigator:
    def __init__(self, serial: str):
        self.serial = serial
        cfg = Config()
        self.url = cfg.get_link()

    def open_external_page(self, wait_time: float = 3.0):
        return open_external_url(self.serial, self.url, wait_time)

    def wait_for_webpage_load(self, timeout: float = 10.0):
        if not wait(self.serial, "link_page_loaded.png", timeout=timeout):
            log_msg(self.serial, "網頁加載逾時")
            return False
        log_msg(self.serial, "網頁載入成功")
        return True

    def scroll_until_run_button(self, max_scrolls: int = 5):
        for i in range(max_scrolls):
            if exist(self.serial, "link_page_run_game.png"):
                return True
            drag(self.serial, (600, 500), (600, 200), wait_time=2.0)
        return False

    def click_run_game(self):
        if exist_click(self.serial, "link_page_run_game.png"):
            log_msg(self.serial, "已點擊 Run Game 按鈕")
            return True
        else:
            log_msg(self.serial, "找不到 Run Game 按鈕")
            return False

    def run(self):
        if self.url == "":
            log_msg(self.serial, "沒有要開啟的網址，跳過")
            return
        if not self.open_external_page():
            log_msg(self.serial, "無法開啟外部網址")
            return
        if not self.wait_for_webpage_load():
            log_msg(self.serial, "無法開啟外部網址")
            return
        if not self.scroll_until_run_button():
            log_msg(self.serial, "無法開啟外部網址")
            return
        if not self.click_run_game():
            log_msg(self.serial, "無法開啟外部網址")
            return

        if not wait(self.serial, "settings_btn.png"):
            launch_game(self.serial)