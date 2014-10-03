# -*- coding: utf-8 -*-
import pytest
from .conftest import DebugRunner, DEBUG_RUNNER_PATH


class TestRunner(object):
    @pytest.mark.migrator(runner_path=DEBUG_RUNNER_PATH)
    def test_load(self, migrator):
        "the runner should be loaded and initialized at runtime"
        assert isinstance(migrator.runner, DebugRunner)

    @pytest.mark.migrator(runner_path=DEBUG_RUNNER_PATH, extra=['initialized'])
    def test_initialize(self, migrator):
        "the runner should be initialized with passed arguments"
        assert migrator.runner.args == ['initialized']
