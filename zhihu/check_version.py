# -*- encoding: utf-8 -*-
import shutil
import os
from webdriver_manager.chrome import ChromeDriverManager


dir_path = os.path.dirname(__file__)
chrome_driver_path = ChromeDriverManager().install()
shutil.move(chrome_driver_path, os.path.join(dir_path, "chromedriver.exe"))
