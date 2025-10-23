import os
from typing import Optional, Type, TypeVar, Union

T = TypeVar("T")

def _env(
    key: str,
    default: Optional[Union[str, int, float, bool]] = None,
    cast: Type[T] = str,
) -> T:
    """
    Recupera uma variável de ambiente com tipagem e valor padrão.

    Args:
        key: Nome da variável de ambiente.
        default: Valor usado se a variável não estiver definida.
        cast: Tipo de conversão (str, int, float, bool).

    Exemplo:
        DEBUG = _env("DEBUG", False, bool)
        TIMEOUT = _env("HTTP_TIMEOUT", 6.0, float)
    """
    value = os.getenv(key)
    if value is None:
        return default  # type: ignore

    if cast == bool:
        return value.lower() in ("1", "true", "yes", "on")  # type: ignore
    try:
        return cast(value)  # type: ignore
    except (TypeError, ValueError):
        return default  # type: ignore
