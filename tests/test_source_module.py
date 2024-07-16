import pytest

from core.modules.source_module import SourceModule


@pytest.fixture
def module_instance():
    return SourceModule('tests/test_source_module.py')


def test_parse_class_imports(module_instance):
    import_name = 'core.modules.source_module'
    module_instance.parse()
    module_instance.select_import(import_name)
    assert isinstance(module_instance.imports[import_name], list)
    assert 'SourceModule' in module_instance.imports[import_name]
