# GTestReport

Pyton 2.* script which generate rather simple HTML output in "out/"directory based on xml gtests repors from "in/" directory.
Clone it and use "generate.(sh|bat)" as startup script. Script was tested with xml output format from gtest-1.7.0.

* Shows in html format status of different tests (failed, succeeded, disabled)
* Shows outline info per each report
* If you give >2 google test xml report then it highlight min and max execution time per test
* If you append custom things into your xml gtest output via "::testing::Test::RecordProperty(key, value);" then this custom fields can be observed in generated report

Screenshot of html report is "screenshot_of_html_report.png"

// Copyright (c) 2016, Konstantin Burlachenko (burlachenkok@gmail.com).  All rights reserved.
