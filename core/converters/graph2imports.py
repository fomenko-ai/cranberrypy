from typing import Dict, List

from pydeps.depgraph import DepGraph, Source

from core.converters.base import AbstractConverter
from core.modules.source_module import SourceModule
from core.modules.import_module import ImportModule
from core.utils.func import write_json
from main import LOGGER


class Graph2Imports(AbstractConverter):

    def _save_dirname(
        self,
        import_name: str,
        import_module: ImportModule
    ):
        if import_module.type:
            self.data["dirnames"][import_name] = import_module.type
        else:
            self.data["dirnames"][import_name] = import_module.dirname

    def _add_import_to_module(
        self,
        module: SourceModule,
        import_name: str,
        values: List[str],
        sources: Dict[str, Source]
    ) -> bool:
        source = sources.get(import_name)
        if source is not None:
            if source.path and (
                source.path.endswith('.py')
                or 'cpython' in source.path
            ):
                _import = ImportModule(source.path)
                if not _import.is_empty:
                    if '*' in values:
                        _import.parse()
                        module.imports[import_name] = _import.identifiers
                    else:
                        module.imports[import_name] = values
                    self._save_dirname(import_name, _import)
                    return True
        else:
            LOGGER.info(f"Module '{import_name}' is absent in pydeps graph.")
        return False

    def _check_relative_source(
        self,
        module: SourceModule,
        sources: Dict[str, Source],
        source_module_name: str
    ):
        for key, values in module.all_imports.items():
            relative_source_name = f'{source_module_name}.{key}'
            if (
                key not in module.imports
                and relative_source_name not in module.imports
                and relative_source_name not in module.all_imports
                and relative_source_name in sources
            ):
                if self._add_import_to_module(
                    module=module,
                    import_name=relative_source_name,
                    values=values,
                    sources=sources
                ):
                    LOGGER.info(
                        f"New module name '{relative_source_name}' is added to imports of '{module.name}' module."
                    )

    def add(self, module: SourceModule, graph: DepGraph):
        if not self.data:
            self.data = {"modules": {}, "dirnames": {}}
        if graph.sources.get(module.name):
            module.parse()

            if module.all_imports:
                for import_name, values in module.all_imports.items():
                    if self._add_import_to_module(
                        module=module,
                        import_name=import_name,
                        values=values,
                        sources=graph.sources
                    ):
                        LOGGER.info(
                            f"'{import_name}' is added to imports of '{module.name}' module."
                        )

            if self.config.relative_source_module:
                self._check_relative_source(
                    module=module,
                    sources=graph.sources,
                    source_module_name=self.config.relative_source_module
                )

            module.check_usages()

            self.data['modules'][module.name] = {
                "imports": module.imports,
                "classes": module.classes,
                "file_path": module.file_path
            }
            self.data["dirnames"][module.name] = module.dirname

    def save(self):
        write_json(
            self.data,
            f"./temp/saved/{self.save_dir}/imports.json"
        )
