"""Helpers para normalizar y validar pagos de comandas."""
from __future__ import annotations

from typing import Dict, Tuple

DEFAULT_METHOD = "efectivo"
PAYMENT_FIELD_BY_METHOD = {
    "efectivo": "monto_efectivo",
    "tarjeta_debito": "monto_tarjeta_debito",
    "tarjeta_credito": "monto_tarjeta_credito",
    "transferencia": "monto_transferencia",
}
PAYMENT_FIELDS = tuple(PAYMENT_FIELD_BY_METHOD.values())


class PaymentError(ValueError):
    """Error lanzado cuando los montos de pago no son válidos."""


def _coerce_amount(value) -> int:
    """Convierte cualquier valor numérico/str a entero positivo."""
    if value in (None, ""):
        return 0
    try:
        return max(int(value), 0)
    except (TypeError, ValueError) as exc:
        raise PaymentError("Monto inválido en pago mixto") from exc


def _normalize_method(methodo: str | None) -> str:
    method = (methodo or "").strip().lower()
    if method == "mixto":
        return method
    if method not in PAYMENT_FIELD_BY_METHOD:
        return DEFAULT_METHOD
    return method


def calculate_payment_breakdown(
    method: str | None,
    total: int,
    montos: Dict[str, int | str | None],
) -> Tuple[str, Dict[str, int]]:
    """Devuelve el método normalizado y los montos por forma de pago."""
    if total < 0:
        raise PaymentError("El total de la comanda no puede ser negativo")

    normalized_method = _normalize_method(method)
    breakdown = {field: 0 for field in PAYMENT_FIELDS}

    if normalized_method == "mixto":
        for field in PAYMENT_FIELDS:
            breakdown[field] = _coerce_amount(montos.get(field))
        if sum(breakdown.values()) != total:
            raise PaymentError("La suma de los montos no coincide con el total")
        if not any(breakdown.values()):
            raise PaymentError("Debe indicar al menos un monto para el pago mixto")
    else:
        field = PAYMENT_FIELD_BY_METHOD[normalized_method]
        breakdown[field] = total

    return normalized_method, breakdown


__all__ = [
    "PaymentError",
    "calculate_payment_breakdown",
]
