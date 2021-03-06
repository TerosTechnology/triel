import os

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import JSONField
from rest_framework.relations import SlugRelatedField

from triel.server.manager.models.master_enuml import SuiteNames, SimulatorNames
from triel.server.manager.models.master_model import Simulator, Suite
from triel.server.manager.models.test_enum import ParameterDataTypeChoices, FileTypeChoices
from triel.server.manager.models.test_model import File, Test, \
    ParameterValue, SimulatorArgument
from triel.suite.cocotb_launcher import launch_cocotb_test
from triel.suite.edalize_launcher import validate_tool_options, validate_edalize_args, launch_edalize_test
from triel.suite.vunit_launcher import launch_vunit_test


def search_before_create(model, validated_data):
    db_data = model.objects.filter(**validated_data)
    if db_data:
        return db_data[0]
    else:
        return model.objects.create(**validated_data)


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
        extra_kwargs = {
            'name': {'validators': []},
        }

    def validate(self, attrs):
        if os.path.exists(attrs['name']):
            return attrs
        else:
            raise ValidationError("Invalid name")


class ParameterValueSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        try:
            datatype = attrs['parameter'].datatype
            if 'default' in attrs.keys():
                attrs['default'] = self.validate_by_datatype(datatype, attrs['default'])
            if 'configure' in attrs.keys():
                attrs['configure'] = self.validate_by_datatype(datatype, attrs['configure'])
            if 'run' in attrs.keys():
                attrs['run'] = self.validate_by_datatype(datatype, attrs['run'])

        except Exception:
            raise ValidationError("Invalid value for this datatype")

    @staticmethod
    def validate_by_datatype(datatype, value):
        if datatype == ParameterDataTypeChoices.bool:
            return bool(value)
        elif datatype == ParameterDataTypeChoices.int:
            return int(value)
        elif datatype in (ParameterDataTypeChoices.str, ParameterDataTypeChoices.file):
            return str(value)


class SimulatorArgumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulatorArgument
        fields = '__all__'
        validators = []


class TestSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True)
    parameters = ParameterValueSerializer(many=True, required=False)
    suite = SlugRelatedField(many=False, queryset=Suite.objects.all(), slug_field='name', required=False)
    tool = SlugRelatedField(many=False, queryset=Simulator.objects.all(), slug_field='name', required=False)
    tool_options = SimulatorArgumentSerializer(many=True, required=False)
    result = JSONField(required=False)

    class Meta:
        model = Test
        fields = '__all__'

    def validate_working_dir(self, wd):
        if os.path.exists(wd):
            return wd
        else:
            raise ValidationError("Invalid name")

    def validate(self, attrs):
        if 'suite' not in attrs.keys():
            attrs['suite'] = Suite.objects.filter(name=SuiteNames.EDALIZE.value)[0]

        tool = attrs.get('tool', '')
        if tool:
            tool = tool.name
        if tool not in (simulator.name for simulator in attrs['suite'].simulators.all()):
            raise ValidationError(f"Invalid simulator {tool} for suite {attrs['suite'].name}")

        if attrs['suite'].name == SuiteNames.EDALIZE.value and 'name' not in attrs.keys():
            raise ValidationError(f"Field name required for {attrs['suite'].name}")

        if attrs['suite'].name == SuiteNames.EDALIZE.value:
            if 'tool_options' in attrs.keys() and \
                    not validate_tool_options(attrs['tool'].name, attrs['tool_options']):
                raise ValidationError(f"Invalid tool options group for tool {attrs['tool']}")
            if 'parameters' in attrs.keys() and \
                    not validate_edalize_args(attrs['tool'].name, attrs['parameters'].parameter):
                raise ValidationError(f"Invalid parameter type for tool {attrs['tool']}")

        if attrs['suite'].name == SuiteNames.VUNIT.value:
            if len(attrs['files']) != 1:
                raise ValidationError(f"Only one file allowed for {attrs['suite'].name} ")
            elif attrs['files'][0]['file_type'] != FileTypeChoices.py.value:
                raise ValidationError("Invalid file type")

        return super(TestSerializer, self).validate(attrs)

    def create(self, validated_data):

        if not validated_data['working_dir'].endswith(os.sep):
            validated_data['working_dir'] += os.sep

        file_list = validated_data.pop('files', ())
        tool_options_list = validated_data.pop('tool_options', ())
        parameters = validated_data.pop('parameters', ())

        test = Test.objects.create(**validated_data)
        test.files.set([search_before_create(File, file) for file in file_list])
        test.tool_options.set([search_before_create(SimulatorArgument, tool_opt) for tool_opt in
                               tool_options_list])
        test.parameters.set([search_before_create(ParameterValue, parameter) for parameter in
                             parameters])

        add_waveform(test)

        {
            SuiteNames.EDALIZE.value: launch_edalize_test,
            SuiteNames.COCOTB.value: launch_cocotb_test,
            SuiteNames.VUNIT.value: launch_vunit_test,
        }.get(validated_data['suite'].name)(test)

        test.save()

        return test


def add_waveform(test: Test):
    if test.tool.name == SimulatorNames.GHDL.value:
        if test.suite.name == SuiteNames.COCOTB.value:
            test.tool_options.add(search_before_create(SimulatorArgument, {"group": "--vcd", "argument": "dump.vcd"}))
        elif test.suite.name == SuiteNames.EDALIZE.value:
            test.tool_options.add(
                search_before_create(SimulatorArgument, {"group": "run_options", "argument": "--vcd=dump.vcd"}))
