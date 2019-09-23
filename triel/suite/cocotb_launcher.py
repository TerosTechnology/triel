import os

from cocotb_test.run import run

from triel.server.manager.models.test_model import Test, FileTypeChoices
from triel.simulator.validator import SimulatorNames


def generate_relative_imports(wd, filepath):
    if wd in filepath:
        extra_route = filepath.split(wd)[1].rsplit('.')[0]
        relative_import_path = ""
        for folder in extra_route.split(os.sep):
            relative_import_path += folder + "."
        return relative_import_path[:-1]


def separate_src_and_modules(files):
    src_list = []
    module_list = []

    for file in files:
        if file.file_type in (FileTypeChoices.vhdl08.value, FileTypeChoices.vlog05.value):
            src_list.append(file.name)
        elif file.file_type == FileTypeChoices.py.value:
            module_list.append(file.name)

    return src_list, module_list


def launch_cocotb_test(test: Test):
    os.environ["SIM"], language, source_arg = {
        SimulatorNames.GHDL.value: ("ghdl", "vhdl", "vhdl_sources"),
        SimulatorNames.ICARUS.value: ("icarus", "verilog", "verilog_sources"),
    }.get(test.tool.name)

    src_list, module_list = separate_src_and_modules(test.files.all())

    modules = ""
    for module in module_list:
        modules += generate_relative_imports(test.working_dir, module) + ','
    modules = modules[:-1]

    simulator_args = []
    for sarg in test.tool_options.all():
        text = sarg.group
        if sarg.argument:
            text += "=" + sarg.argument
        simulator_args.append(text)

    args = {
        source_arg: src_list,
        "toplevel": test.top_level,
        "module": modules,
        "toplevel_lang": language,
        "run_dir": test.working_dir,
        "simulator_args": simulator_args
    }

    sim_result = run(**args)

    test.result = ""
    with open(sim_result) as file:
        for line in file:
            test.result += line
