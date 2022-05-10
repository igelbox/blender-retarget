import sys
import unittest

import coverage

cov = coverage.Coverage(
    branch=True,
    source=['animation_retarget'],
)
cov.start()

suite = unittest.defaultTestLoader.discover('.')
if not unittest.TextTestRunner().run(suite).wasSuccessful():
    sys.exit(1)

cov.stop()
cov.xml_report()

if '--save-html-report' in sys.argv:
    cov.html_report()
