from typing import Any

from pydantic import BaseModel, ConfigDict, alias_generators


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=alias_generators.to_camel, populate_by_name=True)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True)
