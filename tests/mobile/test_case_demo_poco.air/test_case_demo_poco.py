# -*- encoding=utf8 -*-
__author__ = "cooperd"

from airtest.core.api import *
from poco.drivers.android.uiautomation import AndroidUiautomationPoco
import time

auto_setup(__file__, logdir=True, devices=["android://127.0.0.1:5037/R5CW23068CJ?cap_method=ADBCAP&touch_method=MAXTOUCH&",])

# 初始化poco
poco = AndroidUiautomationPoco(use_airtest_input=True, screenshot_each_action=False)

# script content
print("start...")


# generate html report
# from airtest.report.report import simple_report
# simple_report(__file__, logpath=True)
poco("com.android.systemui:id/home").click()
poco("com.android.systemui:id/home").swipe([-0.3386, -0.7387])
time.sleep(3)

poco(text="Youkey Life").click()

poco("家庭\n第 1 个标签，共 4 个").click()
poco("事件\n第 2 个标签，共 4 个").click()
poco("安全模式\n第 3 个标签，共 4 个").click()
poco("账号\n第 4 个标签，共 4 个").click()
poco("家庭\n第 1 个标签，共 4 个").click()
poco("com.android.systemui:id/back").click()
poco("com.android.systemui:id/back").click()

