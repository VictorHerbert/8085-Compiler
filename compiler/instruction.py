from subprocess import call
from typing import List, Union

from .tokens import *

class Instruction:

    def __init__(self,
        argument_list: List[str],
        length : Union[int, callable],
        assemble : callable
    ) -> None:

        self.argument_list = argument_list
        
        self.length = length if callable(length) \
            else lambda _ : length

        self.assemble = assemble

