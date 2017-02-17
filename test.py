import unittest
loader = unittest.TestLoader()
tests = loader.discover('tests', pattern='test_*.py', top_level_dir='.')
testRunner = unittest.TextTestRunner()
testRunner.run(tests)
