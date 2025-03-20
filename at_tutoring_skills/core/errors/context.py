

from dataclasses import dataclass, field

from typing import List



@dataclass(kw_only=True)
class Context:
    parent: "Context" = field(default=None, repr=False)
    name: str

    def create_child(self, name):
        return Context(parent=self, name=name)

    @property
    def full_path_list(self) -> List[str]:
        return self.parent.full_path_list + [self.name] if self.parent else [self.name]



class StudentMistakeException(Exception):
    msg: str
    context: Context
    tip: str


    # fine: None
    def __init__(self, msg, context: Context, *args):
        super().__init__(msg, *args)
        self.context = context
        # self.fine = None