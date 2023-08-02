"""YAMLParams class definition module."""

import os
import io
from datetime import datetime as dt

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.scalarfloat import ScalarFloat


class YAMLParams():
    """Object with YAML-saved parameters."""

    def __init__(self, name, config_dir=None, params=None, load_file=True):
        """YAMLParams object Initializer.

        Parameters
        ----------
        name : string
            Identifier for object.
        config_dir : string, optional
            path to directory containing name.yaml, by default None
        params : dict, optional
           dictionary of parameters with which to initialize, by default None
        load_file : bool, optional
            whether or not to load from the YAML file matching config_dir/[name].yaml

        Raises
        ------
        TypeError
            Raised if name is not a string.
        TypeError
            Raised if config_dir is not a string.
        TypeError
            Raised if params is not a dict.
        """

        # Check type of positional arguments used in this method

        if not isinstance(name, str):
            raise TypeError('YAMLParams object initialization "name" is not an '
                            'instance of string')
        self._yaml = YAML(typ='rt', )
        self._yaml.preserve_quotes = True
        self._yaml.default_flow_style = False
        self._yaml.preserve_quotes = True

        # Set default values of attributes

        self._name = name
        self._params_yaml_dir = os.path.abspath(os.path.curdir)
        self._params_yaml_filepath = \
            os.path.abspath(os.path.join(self._params_yaml_dir,
                                         self._name + '.yaml'))
        self.create_default_params_yaml()
        self.params = self.ryaml_to_pythonic_dict(self._params_yaml['params'])

        # Override optional keyword arguments if not None

        if params is None:
            if config_dir is not None:
                if isinstance(config_dir, str):
                    self._params_yaml_dir = os.path.abspath(config_dir)
                    self._params_yaml_filepath = \
                        os.path.abspath(os.path.join(self._params_yaml_dir,
                                                     self._name + '.yaml'))
                else:
                    raise TypeError('YAMLParams object initialization argument '
                                    '"config_file" is not an instance of string.')
            else:
                self._params_yaml_filepath = \
                    os.path.abspath(os.path.join(self._params_yaml_dir,
                                                self._name + '.yaml'))
                self.params = self.ryaml_to_pythonic_dict(self._params_yaml['params'])
            if load_file is True:
                self.read_params_config()
        else:
            if isinstance(params, dict):
                self.create_default_params_yaml(kind="PASSED_PARAM_DICT")
                self.params = params
                self.capture_params()
                self.params = self.ryaml_to_pythonic_dict(self._params_yaml['params'])
            else:
                raise TypeError('YAMLParams object initialization "params" is '
                                'not an instance of dict.')


    def dump_params_yaml(self):
        """Dump YAML formatted params to a string.

        Dumps self._params_yaml using the ruamel.yaml Round-Trip dumper.

        Returns
        -------
        str
            YAML file formatted string with contents of self._params_yaml
        """
        self.capture_params()
        buf = io.StringIO()
        self._yaml.dump(self._params_yaml, buf)
        out = buf.getvalue()
        buf.close()
        return out

    def save_params_yaml(self, filepath=None):
        """Save params to YAML file.

        If the user does not specify a file, this will write a YAML file to the location where
        the file was loaded, overwriting the previous file.  If the user specifies the 
        filepath option, the YAML output will be saved to the specified location.

        Parameters
        ----------
        filepath : str, optional
            filepath to which to save params contents, by default None
        """
        self.capture_params()
        if filepath is None:

            with open(self._params_yaml_filepath,'w', encoding="utf-8") as fh:  # pylint: disable=C0103
                self._yaml.dump(self._params_yaml, fh)
        else:

            with open(filepath, 'w', encoding="utf-8") as fh:  # pylint: disable=C0103
                self._yaml.dump(self._params_yaml, fh)


    def capture_params(self):
        """Translate the plain Python-typed self.params to the ruamel.yaml-typed 
        self._params_yaml.
        """
        self._params_yaml['params'] = self.merge_params_into_yaml(self.params, 
                                                                self._params_yaml['params'])


    def read_params_config(self, config_file=None):
        """Reads a YAML file into the object's params.

        Parameters
        ----------
        config_file : string, optional
            filepath of the YAML file to load, by default None
        """
        if config_file is not None:
            with open(config_file, 'r', encoding="utf-8") as fh:  # pylint: disable=C0103
                self._params_yaml = self._yaml.load(fh)

            self._params_yaml_filepath = os.path.abspath(config_file)
            self._params_yaml_dir, filename = os.path.split(self._params_yaml_filepath)
            self._name = filename.split('.')[0]
        else:
            with open(self._params_yaml_filepath, 'r', encoding="utf-8") as fh:  # pylint: disable=C0103
                self._params_yaml = self._yaml.load(fh)

        self.params = self.ryaml_to_pythonic_dict(self._params_yaml['params'])


    def create_default_params_yaml(self, kind='SELF_GENERATED'):
        """Create default contents for self.params and self._params_yaml.

        This creates an empty params dict and a pre-formatted "info" block
        for when the YAML file is saved.  

        Parameters
        ----------
        kind : str, optional
            the kind of data generated, by default "SELF_GENERATED"
        """

        yaml_dict = {
            'info': {
                'name': self._name,
                'version': "v0.1.0",
                'date': dt.now().strftime("%A, %d. %B %Y %I:%M%p"),
                'author': f"YAMLParams class, kind: {kind}",
                'description': "Test parametters for developing YAMLParams class.",
            },
            'params': {
            }
        }
        buf = io.StringIO()
        self._yaml.dump(yaml_dict, buf)
        self._params_yaml=self._yaml.load(buf.getvalue())
        buf.close()
        self._params_yaml.yaml_set_start_comment(f"Parameters (params) for "
                                                 f"YAMLParams object "
                                                 f"'{self._name}'.")


    def ryaml_to_pythonic_dict(self, obj):
        """Convert a pythonic dict to a ruamel.yaml friendly types.

        Parameters
        ----------
        obj : CommentedMap
            ruamel.yaml dict type w/ other ruamel.yaml types in it.

        Returns
        -------
        dict
            a "Pure-python" (no ruamel.yaml types) version of the input. 
        """
        if isinstance(obj, CommentedSeq):
            obj = list(obj)
            map(self.ryaml_to_pythonic_dict, obj)
        if isinstance(obj, CommentedMap):
            obj = {key:self.ryaml_to_pythonic_dict(item) for key, item in obj.items()}
        if isinstance(obj, ScalarFloat):
            obj = float(obj)

        return obj


    def merge_params_into_yaml(self,param_obj, yaml_obj):
        """Grab self.params and convert contents into self._params_yaml.

        This is a helper function to take changes to the self.params and
        capture them into the ruamel.yaml CommentedMap() that may alaready
        have comments specified in it.

        Parameters
        ----------
        param_obj : dict
            dict of pythonic objects
        yaml_dict : CommentedMap()
            CommentedMap() of ruamel.yaml objects into which to merge param_obj

        Returns
        -------
        CommentedMap()
            the merged contents of param_obj into yaml_dict.
        """
        
        # print(f'MRO for param_obj: {param_obj.__class__.__mro__}')
        # print(f'MRO for yaml_obj: {yaml_obj.__class__.__mro__}')
        if isinstance(param_obj, dict):
            for key, item in param_obj.items():
                # print(f'Processing key: {key}')
                if key in yaml_obj.keys():
                    yaml_obj[key] = \
                        self.merge_params_into_yaml(item, yaml_obj[key])
                else:
                    yaml_obj[key] = self.merge_params_into_yaml(item, type(item)() )
        elif isinstance(param_obj, list):
            # print('found list!')
            yaml_obj = [None]
            yaml_obj *= len(param_obj)
            for i, item in enumerate(param_obj):
                yaml_obj = list(map(self.merge_params_into_yaml,
                                      param_obj, yaml_obj))
            
            buf = io.StringIO()
            self._yaml.dump(yaml_obj, buf)
            yaml_obj = self._yaml.load(buf.getvalue())
            buf.close()
            
            yaml_obj.fa.set_flow_style()
        else:            
            yaml_obj = param_obj

        return yaml_obj
