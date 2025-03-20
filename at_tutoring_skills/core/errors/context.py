

from dataclasses import dataclass

from typing import List, field



@dataclass(kw_only=True)
class Context:
    parent: "Context" = field(default=None, repr=False)
    name: str

    def create_child(self, name):
        return Context(parent=self, name=name)

    @property
    def full_path_list(self) -> List[str]:
        return self.parent.full_path_list + [self.name] if self.parent else [self.name]
