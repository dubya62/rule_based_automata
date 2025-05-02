
from debug import *


class Error:
    def __init__(self, message:str, filename:str, line_number:int):
        self.message = message
        self.filename = filename
        self.line_number = line_number


class ErrorHandler:
    def __init__(self):
        self.errors = []

    def add_error(self, error:Error, fatal:bool=True):
        self.errors.append(error)

        if fatal:
            print("ENCOUNTERED FATAL ERROR!")
            self.finalize()

    def finalize(self):
        """
        If there are any errors, print and exit
        """
        dbg("Checking for errors...")
        if len(self.errors) > 0:
            for error in self.errors:
                print(f"ERROR at {error.filename}:{error.line_number}\n\t{error.message}")
            if not TESTING:
                exit(1)
        dbg("No errors encountered!")

    

ERROR_HANDLER = ErrorHandler()
