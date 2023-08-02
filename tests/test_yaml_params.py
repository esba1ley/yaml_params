"""Tests for `yaml_params` package."""
import os
import pytest
from collections import OrderedDict
from yaml_params import YAMLParams
from datetime import datetime
import filecmp

def test_yamlparams_init_noargs():
    """Test to make sure YAMLParams asserts when no name argument."""
    with pytest.raises(TypeError):
        myObj = YAMLParams()

def test_yamlparams_init_nameonly_nofile():
    """Test to make sure YAMLParams asserts when no file exists."""
    with pytest.raises(FileNotFoundError):
        myObj = YAMLParams("no_file_with_name")

def test_yamlparams_init_load_file_false():
    """Test to make sure YAMLParams iniailizes correctly w/ load_file=False."""
    myObj = YAMLParams("my_obj", load_file=False)
    dt_str = datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
    assert myObj.params == {}

    assert myObj._params_yaml['info']['name'] == 'my_obj'
    assert myObj._params_yaml['info']['version'] == 'v0.1.0'
    assert myObj._params_yaml['info']['date'] == dt_str
    assert myObj._params_yaml['info']['author'] == 'YAMLParams class, kind: SELF_GENERATED'
    assert myObj._params_yaml['info']['description'] == 'Test parametters for developing YAMLParams class.'
    assert myObj._params_yaml['params'] == OrderedDict()


def test_yamlparams_init_load_file_false_dump():
    """test dump_params_yaml() method for a load_file=False object."""
    myObj = YAMLParams("my_obj", load_file=False)
    dt_str = datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
    assert myObj.dump_params_yaml() == (
        f"# Parameters (params) for YAMLParams object 'my_obj'.\n"
        f"info:\n  name: my_obj\n"
        f"  version: v0.1.0\n"
        f"  date: {dt_str}\n"
        f"  author: 'YAMLParams class, kind: SELF_GENERATED'\n"
        f"  description: Test parametters for developing YAMLParams class.\n"
        f"params: {{}}\n"
    )


def test_yamlparams_init_nameonly_w_file():
    startdir = os.path.abspath(os.path.curdir)
    os.chdir(os.path.join(startdir, 'tests', 'inputs'))
    my_obj = YAMLParams("my_obj")
    os.chdir(startdir)
    assert my_obj._name == "my_obj"
    expected_params = {
                        'myint': 42,
                        'myfloat': 2.718281828,
                        'mystring': 'this is a string', 
                        'myintarray': [1,2,3],
                        'mydict': {
                            'myint': 72,
                            'myfloat': 3.1415926,
                            'mystring': 'this is another string',
                            'myfloatarray': [4.0, 5.0, 6.0],
                        }
                       }
    assert my_obj.params == expected_params
    

def test_yamlparams_init_w_config_dir():
    my_obj = YAMLParams("my_obj", config_dir="tests/inputs")
    assert my_obj._name == "my_obj"
    expected_params = {
                        'myint': 42,
                        'myfloat': 2.718281828,
                        'mystring': 'this is a string', 
                        'myintarray': [1,2,3],
                        'mydict': {
                            'myint': 72,
                            'myfloat': 3.1415926,
                            'mystring': 'this is another string',
                            'myfloatarray': [4.0, 5.0, 6.0],
                        }
                       }
    assert my_obj.params == expected_params

def test_yamlparams_dump_loaded_w_comments():
    my_obj = YAMLParams("my_obj", config_dir="tests/inputs")
    assert my_obj.dump_params_yaml() == (
        '# Summary information\n'
        'info:\n  name: "my_name"\n'
        '  version: "v1.0.0"\n'
        '  date: "Saturday, 29. July 2023 02:11AM"\n'
        '  author: "esbailey@me.com"\n'
        '  description: "Test parametters for developing YAMLParams class."\n'
        '\n'
        '# Parameters for use by simualation\n'
        'params:\n'
        '  myint: 42\n'
        '  myfloat: 2.718281828\n'
        '  mystring: "this is a string"  # got a comment here.\n'
        '  myintarray: [1, 2, 3]\n'
        '  mydict:\n'
        '    myint: 72\n'
        '    myfloat: 3.1415926\n'
        '    mystring: "this is another string"\n'
        '    myfloatarray: [4.0, 5.0, 6.0]\n'
    )

def test_yamlparams_init_w_params_dict():
    my_params = {'myfloat':1.234,
                 'mystr':'this is a string.',
                 'mylistoffloats':[1.2,3.4,5.6],
                 'mylistofints':[1,2,3,4,5]
                 }
    my_obj = YAMLParams("my_obj", params=my_params)
    assert my_obj.params == my_params

def test_yamlparams_read_config_file():
    myObj = YAMLParams("my_obj", load_file=False)
    myObj.read_params_config(config_file='tests/inputs/my_obj.yaml')
    assert myObj.dump_params_yaml() == (
        '# Summary information\n'
        'info:\n  name: "my_name"\n'
        '  version: "v1.0.0"\n'
        '  date: "Saturday, 29. July 2023 02:11AM"\n'
        '  author: "esbailey@me.com"\n'
        '  description: "Test parametters for developing YAMLParams class."\n'
        '\n'
        '# Parameters for use by simualation\n'
        'params:\n'
        '  myint: 42\n'
        '  myfloat: 2.718281828\n'
        '  mystring: "this is a string"  # got a comment here.\n'
        '  myintarray: [1, 2, 3]\n'
        '  mydict:\n'
        '    myint: 72\n'
        '    myfloat: 3.1415926\n'
        '    mystring: "this is another string"\n'
        '    myfloatarray: [4.0, 5.0, 6.0]\n'
    )
    expected_params = {
                        'myint': 42,
                        'myfloat': 2.718281828,
                        'mystring': 'this is a string', 
                        'myintarray': [1,2,3],
                        'mydict': {
                            'myint': 72,
                            'myfloat': 3.1415926,
                            'mystring': 'this is another string',
                            'myfloatarray': [4.0, 5.0, 6.0],
                        }
                       }
    assert myObj.params == expected_params
    assert myObj._params_yaml_dir.endswith('tests/inputs')
    assert myObj._params_yaml_filepath.endswith('tests/inputs/my_obj.yaml')

def test_yamlparams_save_params_yaml():
    myObj = YAMLParams('my_obj', config_dir='tests/inputs')
    myObj._params_yaml_dir = os.path.abspath(os.path.curdir)
    myObj._params_yaml_filepath = os.path.join(myObj._params_yaml_dir, 'my_obj_saved.yaml')
    myObj.save_params_yaml()
    assert filecmp.cmp('my_obj_saved.yaml',
                       './tests/expected_outputs/my_obj.yaml')
    os.remove('my_obj_saved.yaml')

def test_yamlparams_edit_string_w_comment():
    myObj = YAMLParams('my_obj', config_dir='tests/inputs')
    myObj.params['mystring'] = 'this is a string, modified'
    myObj.save_params_yaml(filepath=os.path.join(os.path.curdir,'my_obj_saved.yaml'))
    assert filecmp.cmp('my_obj_saved.yaml',
                       './tests/expected_outputs/my_obj_mod_mystring.yaml')
    os.remove('my_obj_saved.yaml')
    
def test_yamlparams_manual_set_params():
    my_obj = YAMLParams('my_obj', load_file=False)
    my_obj.params = {'myint': 1,
                     'myfloat': 1.234, 
                     'mybool': False,
                     'mystr': 'this is a string.',
                     'mylistofints': [1,2,3,4,5],
                     'mylistoffloats': [1.23, 4.56, 7.89],
                     'mylistofbools': [False, True, False, False, True],
                     'mylistofstrs': ['one', 'two', 'three and four', 'five']
                     }
    my_obj.capture_params()
    dt_str = datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
    assert my_obj.dump_params_yaml() == (
       f"# Parameters (params) for YAMLParams object 'my_obj'.\n"
       f"info:\n"
       f"  name: my_obj\n"
       f"  version: v0.1.0\n"
       f"  date: {dt_str}\n"
       f"  author: 'YAMLParams class, kind: SELF_GENERATED'\n"
       f"  description: Test parametters for developing YAMLParams class.\n"
       f"params:\n"
       f"  myint: 1\n"
       f"  myfloat: 1.234\n"
       f"  mybool: false\n"
       f"  mystr: this is a string.\n"
       f"  mylistofints: [1, 2, 3, 4, 5]\n"
       f"  mylistoffloats: [1.23, 4.56, 7.89]\n"
       f"  mylistofbools: [false, true, false, false, true]\n"
       f"  mylistofstrs: [one, two, three and four, five]\n"
    )
