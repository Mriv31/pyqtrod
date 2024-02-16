# helpers.py
from importlib import reload
import __main__

module_names = ["Fourkas", "corr_matrix", "speeds", "ECF", "MSD", "transition_analysis"]

# Dictionary to store functions
all_functions = {}

# Import all modules and functions
for module_name in module_names:
    module = __import__(module_name)
    globals()[module_name] = module
    # Populate the dictionary with functions from the module
    for func_name in [name for name in dir(module) if callable(getattr(module, name))]:
        all_functions[func_name] = getattr(module, func_name)

    # Update the global namespace of the calling file
    setattr(__main__, module_name, module)
    __main__.__dict__.update(all_functions)


def reload_all():
    # Reload all modules
    for module_name in module_names:
        module = globals()[module_name]
        reload(module)

        # Reload all functions from the reloaded module
        for func_name in [
            name for name in dir(module) if callable(getattr(module, name))
        ]:
            all_functions[func_name] = getattr(module, func_name)

        # Update the global namespace of the calling file
        setattr(__main__, module_name, module)
        __main__.__dict__.update(all_functions)


# Initial update of the global namespace of the calling file
setattr(__main__, "Helpers", __import__("Helpers"))
__main__.__dict__.update(all_functions)
