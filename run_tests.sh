#!/bin/bash
behave
allure serve allure-report

#behave -f allure_behave.formatter:AllureFormatter -o results ./features
#allure generate allure/results/ -o allure/report/
#allure open allure/report