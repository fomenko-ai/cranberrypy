import pytest

from core.modules.source_module import SourceModule


@pytest.fixture
def module_instance():
    return SourceModule('test_source_module.py')


def test_parse_class_imports(module_instance):
    import_name = 'core.modules.source_module'
    module_instance.parse_imports(import_name)
    assert isinstance(module_instance.imports[import_name], list)
    assert 'SourceModule' in module_instance.imports[import_name]
