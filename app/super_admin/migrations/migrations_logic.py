import pathlib
import sys
from os import listdir
from os.path import isfile, join


class MigrationsLogic:

    async def list_all(self):
        path = self.__get_scripts_path()
        files = [f.replace(".py", "") for f in listdir(path) if isfile(join(path, f))]
        files.remove("__init__")
        return files

    async def execute(self, migration_name: str, **args):
        full_module_name = "app.super_admin.migrations.scripts." + migration_name
        __import__(full_module_name, locals(), globals())
        migration = sys.modules[full_module_name]
        return await migration.run(**args)

    def __get_scripts_path(self):
        path = pathlib.Path(__file__).parent.absolute()
        path = join(path, "scripts")
        return path
