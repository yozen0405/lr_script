from enum import Enum
from string import Formatter

class Base(str, Enum):
    def __call__(self, **kwargs) -> str:
        # 有給參數就格式化
        if kwargs:
            try:
                return self.value.format(**kwargs)
            except KeyError as e:
                raise ValueError(f"{self.name} 缺少參數: {e.args[0]}，需要 {self.placeholders}")
        # 沒給參數，但樣板其實需要 → 報錯，避免靜默用錯
        if self.placeholders:
            raise ValueError(f"{self.name} 需要參數: {self.placeholders}")
        return self.value

    @property
    def placeholders(self) -> tuple[str, ...]:
        return tuple(
            fname for _, fname, _, _ in Formatter().parse(self.value) if fname
        )

    @property
    def is_dynamic(self) -> bool:
        return bool(self.placeholders)