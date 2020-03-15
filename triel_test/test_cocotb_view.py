"""

 Copyright 2020 Teros Technology

 Ismael Perez Rojo
 Carlos Alberto Ruiz Naranjo
 Alfredo Saez

 This file is part of Triel.

 Triel is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 Triel is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with Colibri.  If not, see <https://www.gnu.org/licenses/>.

"""

import unittest

import requests

from triel.server.manager.models.master_enuml import SimulatorNames, SuiteNames
from triel.server.manager.models.test_enum import FileTypeChoices
from triel_test.resources_test import resource_test_path
from triel_test.test_master_view import TrielTestCase, TRIEL_URL

COCO_URL = TRIEL_URL + 'tests/'


class Coco(TrielTestCase):
    def test_adder_vlog(self):
        data = {
            "suite": SuiteNames.COCOTB.value,
            "working_dir": resource_test_path("scripts/cocotb/simple"),
            "files": [
                {"name": resource_test_path("scripts/cocotb/simple/test_adder.py"),
                 "file_type": FileTypeChoices.py.value},
                {"name": resource_test_path("hdl/adder.v"),
                 "file_type": FileTypeChoices.vlog05.value}
            ],
            "top_level": "adder",
            "tool": SimulatorNames.ICARUS.value,
        }
        response = requests.post(COCO_URL, json=data)
        self.print_response(response)
        assert response.status_code == 201

    def test_adder_vhdl(self):
        data = {
            "suite": SuiteNames.COCOTB.value,
            "working_dir": resource_test_path("scripts/cocotb/simple"),
            "files": [
                {"name": resource_test_path("scripts/cocotb/simple/test_adder.py"),
                 "file_type": FileTypeChoices.py.value},
                {"name": resource_test_path("hdl/adder.vhd"),
                 "file_type": FileTypeChoices.vhdl08.value},
            ],
            "top_level": "adder",
            "tool": SimulatorNames.GHDL.value
        }
        response = requests.post(COCO_URL, json=data)
        self.print_response(response)
        assert response.status_code == 201


if __name__ == '__main__':
    unittest.main()
