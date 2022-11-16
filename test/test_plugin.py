import unittest
from Branching import Plugin

"""
显式加载
import plugin...
依赖传递
import pluginA, -> PluginB
去除插件显式调用
call_before()...
插件优先级
level
去除插件
plugin.remove()
"""


class TestPluginInClass(unittest.TestCase):
    def test_before(self):
        @Plugin
        def target(number: int):
            return number

        @target.before
        def before(number: int):
            return number + 1

        self.assertEqual(target(1), 2)

    def test_after(self):
        @Plugin
        def target(number: int):
            return number

        @target.after
        def after(number: int):
            return number + 1

        self.assertEqual(target(1), 2)


if __name__ == '__main__':
    unittest.main()
