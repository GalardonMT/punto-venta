"""Funciones auxiliares para envío a impresoras térmicas."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    import win32print  # type: ignore
except ImportError:  # pragma: no cover - solo en sistemas sin win32
    win32print = None  # type: ignore


class PrinterError(RuntimeError):
    """Errores relacionados al driver de impresión."""


def send_raw_to_printer(printer_name: str, job_name: str, payload: str) -> None:
    """Envía texto plano a la impresora indicada."""
    if not payload:
        logger.debug("No hay contenido para imprimir en %s", printer_name)
        return

    if win32print is None:
        raise PrinterError("win32print no está disponible en este entorno")

    encoded_payload = payload.encode("utf-8")
    job_title = job_name or "Documento"

    try:
        logger.info("Enviando trabajo '%s' a la impresora %s", job_title, printer_name)
        handle = win32print.OpenPrinter(printer_name)
        try:
            job = win32print.StartDocPrinter(handle, 1, (job_title, None, "RAW"))
            win32print.StartPagePrinter(handle)
            win32print.WritePrinter(handle, encoded_payload)
            win32print.EndPagePrinter(handle)
            win32print.EndDocPrinter(handle)
            logger.info("Trabajo '%s' completado en %s", job_title, printer_name)
        finally:
            win32print.ClosePrinter(handle)
    except Exception as exc:  # pragma: no cover - manejo específico de win32
        logger.exception("No se pudo imprimir en %s", printer_name)
        raise PrinterError(f"Fallo al imprimir en {printer_name}") from exc


__all__ = ["PrinterError", "send_raw_to_printer"]
