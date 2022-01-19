import os
from typing import Callable, List

import yaml

from core.utils.strings import to_pascal


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class MetaItem:

    def __init__(self, name, full_name, class_name, data):
        self.name = name
        self.full_name = full_name
        self.class_name = class_name
        self.data = data

    def __str__(self):
        return str(self.__dict__)


class MetadataParser:

    def __init__(self, name_prefix: str, base_dir=".", source_definitions_name="source.yaml",
                 template_file_names={}):
        self.name_prefix = name_prefix
        self.base_dir = base_dir

        self.source_definitions_name = source_definitions_name
        self.source_definitions = None

        self.template_file_names = template_file_names
        self.templates = {}

    def load_source(self):
        file_path = f"{self.base_dir}\\{self.source_definitions_name}"
        with open(file_path) as f:
            self.source_definitions = yaml.load(f, Loader=yaml.FullLoader)
        return self

    def print_source(self):
        print(f"#### {self.source_definitions_name} ####")
        print(self.source_definitions)

    def load_templates(self):
        for key in self.template_file_names:
            fname = self.template_file_names[key]
            file_path = f"{self.base_dir}\\{fname}"
            self.templates[key] = file_path
            with open(file_path) as f:
                self.templates[key] = f.read()

    def get_template(self, key):
        return self.templates[key]

    def print_templates(self):
        for key in self.templates:
            print(f"#### {key} ####")
            print(f"{self.get_template(key)}")

    def get_raw_source(self):
        return self.source_definitions

    def iterate_source(self):

        for item in self.source_definitions:
            full_name = f"{self.name_prefix}_{item}"
            class_name = f"{to_pascal(self.name_prefix)}_{to_pascal(item)}"
            yield MetaItem(item, full_name, class_name, self.source_definitions[item])

    def get_source_as_object(self):
        result = {}
        for item in self.iterate_source():
            result[item.name] = item
        return Struct(result)

    def get_source_as_array(self):
        result = []
        for item in self.iterate_source():
            result.append(item)
        return result

    def test(self):
        self.load_source()
        self.load_templates()

        for item in self.iterate_source():
            print(item)

        print(os.linesep)
        self.print_templates()


class GeneratorBlock:

    def __init__(self, base_dir, dest_file_name, generator_function: Callable, **extra_params):
        self.generator_function = generator_function
        self.extra_params = extra_params
        self.dest_file = open(f"{base_dir}\\{dest_file_name}", "w")

    def generate(self, metadata_parser: MetadataParser, meta_item: MetaItem):
        txt = self.generator_function(metadata_parser, meta_item, **self.extra_params)
        self.dest_file.write(txt)

    def cleanup(self):
        self.dest_file.close()


class Generator:
    # Usage
    """

    BASE_DIR = "C:\\work\\ignilife\\alakine-be\\app\\feed\\samples"

    generator_blocks = []
    generator_blocks.append(GeneratorBlock(BASE_DIR, "output\\__questions_models.py", generate_models))
    generator_blocks.append(GeneratorBlock(
        BASE_DIR,
        "output\\__questions_api.py",
        generate_api,
        api_router_name = "router_tests_questions"))

    metadata_parser = MetadataParser(
        name_prefix="question",
        base_dir=BASE_DIR,
        source_definitions_name="input\\definitions_questions.yaml",
        template_file_names={
            "models": "input\\template_models_messages.py",
            "api": "input\\template_api.py"
        }
    )

    Generator(metadata_parser, generator_blocks) \
        .test() \
        .generate() \
        .cleanup()

    """

    def __init__(self,
                 metadata_parser: MetadataParser,
                 generator_blocks: List[GeneratorBlock],
                 ):

        self.meta = metadata_parser
        self.generator_blocks = generator_blocks

    def cleanup(self):
        for genblock in self.generator_blocks:
            genblock.cleanup()

    def generate(self):

        self.meta.load_source()
        self.meta.load_templates()

        for item in self.meta.iterate_source():
            for genblock in self.generator_blocks:
                genblock.generate(self.meta, item)

        return self

    def test(self):
        self.meta.test()
        return self
