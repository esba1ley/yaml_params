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

        Raises
        ------
        TypeError
            Raised if config_file or name is not a string.
        TypeError
            _description_
        TypeError
            _description_
        """

        # Check type of positional arguments used in this method

        if not isinstance(name, str):
            raise TypeError('YAMLParams object initialization "name" is not an '
                            'instance of string')
        self._yaml = YAML()
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
        """_summary_

        Returns
        -------
        _type_
            _description_
        """
        self.capture_params()
        buf = io.StringIO()
        self._yaml.dump(self._params_yaml, buf)
        out = buf.getvalue()
        buf.close()
        return out

    def save_params_yaml(self, filepath=None):
        """_summary_

        Parameters
        ----------
        filepath : _type_, optional
            _description_, by default None
        """
        self.capture_params()
        if filepath is None:
            with open(self._params_yaml_filepath,'w') as fh:
                self._yaml.dump(self._params_yaml, fh)
        else:
            with open(filepath, 'w') as fh:
                self._yaml.dump(self._params_yaml, fh)


    def capture_params(self):
        """_summary_
        """
        self._params_yaml['params'] = self.populate_params_yaml_from_dict(self.params, 
                                                                self._params_yaml['params'])


    def read_params_config(self, config_file=None):
        """_summary_

        Parameters
        ----------
        config_file : _type_, optional
            _description_, by default None
        """
        if config_file is not None:
            with open(config_file, 'r') as fh:
                self._params_yaml = self._yaml.load(fh)
            
            self._params_yaml_filepath = os.path.abspath(config_file)
            self._params_yaml_dir, filename = os.path.split(self._params_yaml_filepath)
            self._name = filename.split('.')[0]
        else:
            with open(self._params_yaml_filepath, 'r') as fh:
                self._params_yaml = self._yaml.load(fh)

        self.params = self.ryaml_to_pythonic_dict(self._params_yaml['params'])
    

    def create_default_params_yaml(self, kind="SELF_GENERATED"):
        """_summary_

        Parameters
        ----------
        kind : str, optional
            _description_, by default "SELF_GENERATED"
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
        """_summary_

        Parameters
        ----------
        obj : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        if isinstance(obj, CommentedSeq):
            obj = list(obj)
            map(self.ryaml_to_pythonic_dict, obj)
        if isinstance(obj, CommentedMap):
            obj = {key:self.ryaml_to_pythonic_dict(item) for key, item in obj.items()}
        if isinstance(obj, ScalarFloat):
            obj = float(obj)

        return obj
        

    def populate_params_yaml_from_dict(self,param_obj, yaml_obj):
        """_summary_

        Parameters
        ----------
        param_obj : _type_
            _description_
        yaml_dict : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        if isinstance(param_obj, dict):
            for key, item in param_obj.items():
                if key in yaml_obj.keys():
                    yaml_obj[key] = \
                        self.populate_params_yaml_from_dict(item, yaml_obj[key])
                else:
                    yaml_obj[key] = param_obj[key]
        elif isinstance(param_obj, list):
            yaml_obj = list(map(self.populate_params_yaml_from_dict,
                                      param_obj, yaml_obj))
            
            buf = io.StringIO()
            self._yaml.dump(yaml_obj, buf)
            yaml_obj = self._yaml.load(buf.getvalue())
            buf.close()
            
            yaml_obj.fa.set_flow_style()
        else:            
            yaml_obj = param_obj

        buf = io.StringIO()
        self._yaml.dump(yaml_obj, buf)
        yaml_obj = self._yaml.load(buf.getvalue())
        buf.close()

        return yaml_obj
