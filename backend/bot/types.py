from typing import TypeVar

_T = TypeVar('_T')


def expect(value: _T | None) -> _T:
    if value is None:
        raise ValueError('Value cannot be None')
    return value
