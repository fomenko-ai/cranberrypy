import pytest

from core.modules.import_module import ImportModule


@pytest.fixture
def module_instance(tmp_path):
    d = tmp_path / "subdirectory"
    d.mkdir()
    f = d / "test.py"
    f.write_text('import os\nfrom sys import path')
    return ImportModule(str(f))


def test_initial_type_none(module_instance):
    assert module_instance.type is None


def test_initial_empty_check(module_instance):
    assert module_instance.is_empty is False


def test_initial_imports_check(module_instance):
    assert module_instance.has_imports is True


def test_get_type_built_in(module_instance):
    module_instance._ImportModule__get_type('/usr/lib/python3.8/http')
    assert module_instance.type == 'built_in'


def test_get_type_third_party(module_instance):
    module_instance._ImportModule__get_type('/home/user/.local/lib/python3.8/site-packages/requests')
    assert module_instance.type == 'third_party'


def test_get_type_none(module_instance):
    module_instance._ImportModule__get_type('/home/user/project/module.py')
    assert module_instance.type is None


def test_check_imports(module_instance):
    assert module_instance.has_imports is True
