#!/bin/bash
#behave -f allure_behave.formatter:AllureFormatter -o allure-report/results ./features
behave

#cp -R allure/reports/history allure/results/history

#allure generate allure-report/results/ -o allure-report/reports
#allure open allure-report/reports
allure serve allure-report


#behave -f allure_behave.formatter:AllureFormatter -o results ./features
#allure generate allure/results/ -o allure/report/
#allure open allure/report