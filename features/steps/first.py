from behave import *
from selenium.webdriver.common.by import By

use_step_matcher("parse")


@step("находимся на сайте '{url}'")
def step_impl(context, url):
    context.logger.debug("url: {}".format(url))
    context.browser.get(url)


@step("кликнем '{btn_text}'")
def step_impl(context, btn_text):
    context.logger.debug("кликаем: {}".format(btn_text))
    elem = context.browser.find_element(By.CSS_SELECTOR, "div.FPdoLc input.RNmpXc")
    elem.click()


@step("будет ссылка '{a_text}'")
def step_impl(context, a_text):
    context.logger.debug("ищем ссылку: {}".format(a_text))
    context.browser.find_element_by_link_text(a_text).click()