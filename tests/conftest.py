# -*- coding: utf-8 -*-
import pytest

TEST_COMMENTS = ['#', '--', '//', ';', '"']

@pytest.fixture(params=TEST_COMMENTS)
def up_stmt(request):
    return '%s MIGRATE UP' % request.param

@pytest.fixture(params=TEST_COMMENTS)
def down_stmt(request):
    return '%s MIGRATE DOWN' % request.param
