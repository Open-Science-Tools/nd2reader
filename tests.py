"""
Auto-discovers all unittests in the tests directory and runs them

"""
import unittest
loader = unittest.TestLoader()
tests = loader.discover('tests', pattern='*.py', top_level_dir='.')
testRunner = unittest.TextTestRunner()
testRunner.run(tests)