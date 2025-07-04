from dataclasses import dataclass
import json
from typing import Any


def parse_str(*args: str):
    joined = ""
    for line in args[: len(args) - 1]:
        joined += line + "\n"
    return joined + args[len(args) - 1]

def json_construct(file_name:str):
    base = ""
    with open(file_name,"r") as file:
        content = json.load(file)
        for key,value in content.items():
            join = ""
            mapped_string = list(map(lambda x:"    "+x,value["docstring"]))
            docstring = f"    '''\n{parse_str(*mapped_string)}\n    '''"
            for name,value in value["attr"].items():
                join += f"    {name} = {value}\n"
                
            base += parse_str(
                f"class {key}:",
                f"{docstring}",
                f"{join}\n"
            )
    return base
        
@dataclass
class pair:
    """
    Base of arguments and value for the module.
    attributes:
        class_type:The type of object the value is.
        value:The value of the object. 
            When used with Minimal class, using a singleton tuple, example:(1,) , it will return the name for getting constructor arguments.
    """
    class_type: type = Any
    value: Any = None

def declare(**variables):
    """
    Returns a string object with variables provided by the 'variables' argument set.
    When creating variables, always use the 'pair' dataclass.
    example: ```declare(x = pair(10))```
    """
    join = ""
    for key, value_pair in variables.items():
        value_pair: pair
        if isinstance(value_pair.value, str):
            join += f"{key}:{value_pair.class_type.__name__} = '{value_pair.value}'\n"
        elif value_pair.class_type == Any:
            join += f"{key}:{type(value_pair.value).__name__} = {value_pair.value}\n"
    
    return join

def MinimalClass(name:str,instance_name:str = "self",arguments:dict = {},**class_attributes):
    """
    Returns a minimal class setup based on the arguments provided.
    name: name of the class
    instance_name: name of the instance representor. Defaults to 'self'.
    arguments: The arguments provided to in the constructor. Defaults to {}.
    class_attributes: The attributes the class has.
    """
    passed_args = ""
    instance_variables = ""
    
    for key,value_pair in arguments.items():
        value_pair:pair
        if value_pair.value == None:
            passed_args += f"{key}:{value_pair.class_type.__name__},"
        else:
            passed_args += f"{key}:{value_pair.class_type.__name__} = {value_pair.value},"
            
    for key,value_pair in class_attributes.items():
        if isinstance(value_pair.value,str):
            instance_variables += f"        {instance_name}.{key}:{value_pair.class_type.__name__} = '{value_pair.value}'\n"
        elif isinstance(value_pair.value,tuple):
            instance_variables += f"        {instance_name}.{key}:{value_pair.class_type.__name__} = {value_pair.value[0]}\n"
        else:
            instance_variables += f"        {instance_name}.{key}:{value_pair.class_type.__name__} = {value_pair.value}\n"
          
    passed_args = passed_args[:len(passed_args)-1]
      
    if len(arguments) > 0:base = parse_str(
        f"class {name}:",
        f"    def __init__({instance_name},{passed_args}):",
        instance_variables,
        "        pass"
    )
    else:base = parse_str(
        f"class {name}:",
        f"    def __init__({instance_name}):",
        instance_variables,
        "        pass"
    )
    return base

def Structure(name: str, **attr: dict[str, pair]):
    """
    Returns a string object with its content representing a mutable class.
    The class's constructor is a tuple, as it provides the proper structure needed.
    Note all values in the class are mutable, the reason is because the contents of the object can be changed, but the object cannot be changed.
    ```
    #example
    my_tuple = ([],2)
    print(my_tuple) #output:([],2)
    my_tuple[0].append(10)
    print(my_tuple) #output:([10],2)
    ```
    
    The name argument represents the name of the class.
    the attr keyword argument set represents the objects inside the class. All values part of the attr keyword argument set must be a pair object.
    """
    args = ""
    tuple_iter = "("
    joined = ""
    index = 0
    for key, value_pair in attr.items():
        value_pair: pair
        if value_pair.value == None:
            args += f"{key}:{value_pair.class_type.__name__},"
        else:
            args += f"{key}:{value_pair.class_type.__name__} = {value_pair.value},"
        tuple_iter += f"mutable({key}),"

        joined += (
            parse_str(
                f"    @property",
                f"    def {key}(self):",
                f"        return self[{index}].value\n",
                f"    @{key}.setter",
                f"    def {key}(self,new_value):",
                f"        self[{index}].value = new_value\n",
            )
            + "\n"
        )
        index += 1

    args = args[: len(args) - 1]
    tuple_iter = tuple_iter[: len(tuple_iter) - 1] + ")"

    base = parse_str(
        f"class {name}(tuple):",
        f"    def __new__(cls,{args}):",
        f"        return super().__new__(cls,{tuple_iter})\n",
        joined
    )
    return base


def lambda_template(name:str,**arguments):
    args = ""
    for key,pair_value in arguments.items():
        pair_value:pair
        if pair_value.value == None:
            args += f"{key},"
        else:
            args += f"{key} = {pair_value.value},"
        
    args = args[:len(args)-1]
    return f"{name} = lambda {args}:0"


def function_template(name:str,indent:str = "",function_type:type = None,**arguments):
    args = ""
    for key,pair_value in arguments.items():
        pair_value:pair
        if pair_value.value == None:
            args += f"{key}:{pair_value.class_type.__name__},"
        elif isinstance(pair_value.value,str):
            args += f"{key}:{pair_value.class_type.__name__} = '{pair_value.value}',"
        else:
            args += f"{key}:{pair_value.class_type.__name__} = {pair_value.value},"
        
    args = args[:len(args)-1]
    if function_type == None:return parse_str(
        f"{indent}def {name}({args}):",
        f"{indent}    return 0"
    )
    else:return parse_str(
        f"{indent}@{function_type.__name__}",
        f"{indent}def {name}({args}):",
        f"{indent}    return 0"
    )


def add_import(module_name:str):
    return f"import {module_name}\n"


def new_string_body(file_name: str, *template: str):
    f"""
    Creates a new file with the name provided.
    Uses the template argument set to create the file.
    Uses the file_name argument to declare the name of the file.
    """
    join = ""
    with open(file_name, "w") as file:
        for content in template:
            join += content + "\n"
        file.write(
            parse_str(
                "from dataclasses import dataclass",
                "from typing import Any",
                "from types import NoneType\n",
                "@dataclass",
                "class mutable:",
                "    value:Any\n",
                join,
            )
        )
