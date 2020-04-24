import os
import shutil
import time
import logging
from datetime import datetime
from selenium import webdriver
import allure_commons
from allure_commons.types import AttachmentType
from allure_commons.utils import now, uuid4
from allure_commons.model2 import Status
from allure_commons.model2 import TestResult
from allure_commons.model2 import TestStepResult
from allure_commons.logger import AllureFileLogger
from allure_commons.reporter import AllureReporter

# behave -D BROWSER=chrome -D ARCHIVE=Yes

PROJECT_NAME = "behave_tests"
DEFAULT_BROWSER = "chrome"
LOG_DIR = "logs"
ALLURE_REPORT_DIR = "allure-report"


def before_all(context):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    report_dir_name = ALLURE_REPORT_DIR
    context.allure = AllureReporter()
    file_logger = AllureFileLogger(report_dir_name)
    allure_commons.plugin_manager.register(file_logger)


def before_feature(context, feature):
    # Create logger
    context.logger = logging.getLogger(PROJECT_NAME)
    handler = logging.FileHandler('.' + os.sep + LOG_DIR + os.sep + PROJECT_NAME + '.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(formatter)
    context.logger.addHandler(handler)
    context.logger.setLevel(logging.DEBUG)
    context.logger.debug("> feature '{}'".format(feature.name))


def before_scenario(context, scenario):
    context.case_uuid = uuid4()
    context.testcase = TestResult(
        uuid=context.case_uuid,
        start=now(),
        fullName=scenario.name)
    context.allure.schedule_test(context.case_uuid, context.testcase)

    context.logger.debug("user data: {}".format(context.config.userdata))
    # behave -D BROWSER=chrome
    if 'BROWSER' in context.config.userdata.keys():
        if context.config.userdata['BROWSER'] is None:
            BROWSER = DEFAULT_BROWSER
        else:
            BROWSER = context.config.userdata['BROWSER']
    else:
        BROWSER = DEFAULT_BROWSER

    if BROWSER == 'chrome':
        context.browser = webdriver.Chrome()
    elif BROWSER == 'firefox':
        context.browser = webdriver.Firefox()
    elif BROWSER == 'safari':
        context.browser = webdriver.Safari()
    elif BROWSER == 'ie':
        context.browser = webdriver.Ie()
    elif BROWSER == 'opera':
        context.browser = webdriver.Opera()
    elif BROWSER == 'phantomjs':
        context.browser = webdriver.PhantomJS()
    else:
        context.logger.error("Browser you entered: " + BROWSER + " is invalid value")

    context.browser.maximize_window()
    context.browser.implicitly_wait(5)
    context.logger.debug(">> scenario '{}'".format(scenario.name))


def before_step(context, step):
    context.logger.debug(">>> step '{}'".format(step.name))
    allure_step = TestStepResult(name=step.name, start=now())
    context.current_step_uuid = uuid4()
    context.allure.start_step(None, context.current_step_uuid, allure_step)


def after_step(context, step):
    context.logger.debug(">>> step '{}' {}".format(step.name, step.status))

    if step.status == "passed":
        my_status = Status.PASSED
    elif step.status == "skipped":
        my_status = Status.SKIPPED
    elif step.status == "undefined":
        my_status = Status.BROKEN
    else:
        my_status = Status.FAILED
        noww = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        context.logger.debug(f"take step Screenshot-{noww}")
        context.allure.attach_data(
            context.current_step_uuid,
            context.browser.get_screenshot_as_png(),
            name=f"Screenshot-step-{noww}", attachment_type=AttachmentType.PNG)
    context.allure.stop_step(context.current_step_uuid, stop=now(), status=my_status)


def after_scenario(context, scenario):
    context.logger.debug(">> scenario '{}' {}".format(scenario.name, scenario.status))

    if scenario.status == "failed":
        noww = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        context.logger.debug(f"take Screenshot-{noww}")
        context.allure.attach_data(
            context.case_uuid,
            context.browser.get_screenshot_as_png(),
            name=f"Screenshot-{noww}", attachment_type=AttachmentType.PNG)
        context.testcase.status = Status.FAILED
    elif scenario.status == "skipped":
        context.testcase.status = Status.SKIPPED
    elif scenario.status == "untested":
        context.testcase.status = Status.BROKEN
    else:
        context.testcase.status = Status.PASSED
    context.testcase.stop = now();

    context.allure.close_test(context.case_uuid)
    context.browser.delete_all_cookies()
    context.browser.close()
    context.browser.quit()


def after_feature(context, feature):
    context.logger.debug("> feature '{}' {}".format(feature.name, feature.status))


def after_all(context):
    # behave -D ARCHIVE=Yes
    if 'ARCHIVE' in context.config.userdata.keys():
        if context.config.userdata['ARCHIVE'] == "Yes":
            context.logger.debug("Create zip archive")
            shutil.make_archive(
                time.strftime("%d_%m_%Y"),
                'zip',
                "screenshots")
