from typing import Dict

from pydeps.depgraph import DepGraph, Source

from core.converters.base import AbstractConverter
from core.modules.source_module import SourceModule
from core.modules.import_module import ImportModule
from core.utils.func import write_json
from main import LOGGER


class Graph2Imports(AbstractConverter):

    def _add_dirname(
        self,
        import_name: str,
        import_module: ImportModule
    ):
        if import_module.type:
            self.data["dirnames"][import_name] = import_module.type
        else:
            self.data["dirnames"][import_name] = import_module.dirname

    def _check_import_source(
        self,
        import_name: str,
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
                    self._add_dirname(import_name, _import)
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
                if self._check_import_source(
                    import_name=relative_source_name,
                    sources=sources
                ):
                    module.imports.update({relative_source_name: values})
                    LOGGER.info(
                        f"New module name '{relative_source_name}' is added to imports."
                    )

    def add(self, module: SourceModule, graph: DepGraph):
        if not self.data:
            self.data = {"modules": {}, "dirnames": {}}
        if graph and graph.sources and graph.sources.get(module.name):
            module.parse()
            if module.all_imports:
                for import_name in module.all_imports.keys():
                    if self._check_import_source(
                        import_name,
                        sources=graph.sources
                    ):
                        module.get_import(import_name)

            module.check_usages()

            if self.config.relative_source_module:
                self._check_relative_source(
                    module=module,
                    sources=graph.sources,
                    source_module_name=self.config.relative_source_module
                )

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
