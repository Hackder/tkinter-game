import sys


class CliOptions:
    def _set_log_level(self, value: str):
        if value not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise Exception(f"Unknown log level: {value}")
        self.log_level = value

    def _set_global_log_level(self, value: str):
        if value not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise Exception(f"Unknown log level: {value}")
        self.global_log_level = value

    def __init__(self, args: list[str]):
        self.log_level = "WARNING"
        self.global_log_level = "WARNING"
        self.metrics = False
        self.width = 800
        self.height = 600

        methods = dir(self)

        for arg in args[1:]:
            if arg == "--help" or arg == "-h":
                self._print_help()
                sys.exit(0)

            for name, value in vars(self).items():
                arg_name = f"{self._cli_arg_name(name)}="
                if arg.startswith(arg_name):
                    provided_value = arg[len(arg_name) :]
                    if f"_set_{name}" in methods:
                        getattr(self, f"_set_{name}")(provided_value)
                    else:
                        t = type(value)
                        setattr(self, name, t(provided_value))
                    break
            else:
                print(f"Unknown argument: {arg}")
                self._print_help()
                sys.exit(1)

    def _cli_arg_name(self, name: str) -> str:
        return f"--{name.replace('_', '-')}"

    def _print_help(self):
        print("Usage: python run.py [options]")
        print("Options:")
        methods = dir(self)
        for name, value in vars(self).items():
            if f"_get_{name}" in methods:
                value = getattr(self, f"_get_{name}")()
            print(f"  {self._cli_arg_name(name)}={value}")
