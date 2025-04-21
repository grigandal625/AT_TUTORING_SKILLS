from dataclasses import dataclass
from dataclasses import field


@dataclass(kw_only=True)
class Context:
    parent: "Context" = field(default=None, repr=False)
    name: str

    def create_child(self, name):
        return Context(parent=self, name=name)

    @property
    def full_path_list(self) -> str:
        parts = []
        current = self
        while current:
            parts.append(current.name)
            current = current.parent
        return ".".join(reversed(parts))


class StudentMistakeException(Exception):
    msg: str
    context: Context
    tip: str

    # fine: None
    def __init__(self, msg, context: Context, *args):
        super().__init__(msg, *args)
        self.context = context
        # self.fine = None
