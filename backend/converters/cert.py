"""Conversor de certificados SSL/TLS: PEM ↔ DER ↔ PFX/P12."""
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography import x509
    except ImportError:
        raise RuntimeError("Instale: pip install cryptography")

    input_ext = Path(input_path).suffix.lstrip(".").lower()
    target_format = target_format.lower()
    raw = Path(input_path).read_bytes()

    if input_ext in ("pem", "crt", "cer", "key"):
        _from_pem(raw, output_path, target_format, serialization, x509)
    elif input_ext == "der":
        _from_der(raw, output_path, target_format, serialization, x509)
    elif input_ext in ("pfx", "p12"):
        _from_pfx(raw, output_path, target_format, serialization)
    else:
        raise ValueError(f"Certificado não suporta entrada: {input_ext}")


def _from_pem(raw: bytes, output_path: str, target_format: str, serialization, x509) -> None:
    if target_format == "der":
        cert = x509.load_pem_x509_certificate(raw)
        Path(output_path).write_bytes(cert.public_bytes(serialization.Encoding.DER))

    elif target_format == "pfx":
        # Criar PFX sem chave privada (somente certificado)
        from cryptography.hazmat.primitives.serialization import pkcs12
        cert = x509.load_pem_x509_certificate(raw)
        pfx = pkcs12.serialize_key_and_certificates(
            name=cert.subject.get_attributes_for_oid(
                x509.NameOID.COMMON_NAME
            )[0].value.encode() if cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME) else b"cert",
            key=None,
            cert=cert,
            cas=None,
            encryption_algorithm=serialization.NoEncryption(),
        )
        Path(output_path).write_bytes(pfx)

    elif target_format == "pem":
        # PEM → PEM: normalizar
        Path(output_path).write_bytes(raw)

    else:
        raise ValueError(f"PEM não suporta saída: {target_format}")


def _from_der(raw: bytes, output_path: str, target_format: str, serialization, x509) -> None:
    cert = x509.load_der_x509_certificate(raw)

    if target_format == "pem":
        pem = cert.public_bytes(serialization.Encoding.PEM)
        Path(output_path).write_bytes(pem)

    elif target_format == "pfx":
        from cryptography.hazmat.primitives.serialization import pkcs12
        pfx = pkcs12.serialize_key_and_certificates(
            name=b"cert", key=None, cert=cert, cas=None,
            encryption_algorithm=serialization.NoEncryption(),
        )
        Path(output_path).write_bytes(pfx)

    else:
        raise ValueError(f"DER não suporta saída: {target_format}")


def _from_pfx(raw: bytes, output_path: str, target_format: str, serialization) -> None:
    from cryptography.hazmat.primitives.serialization import pkcs12

    # Tentar sem senha primeiro
    for password in (None, b"", b"changeit", b"password"):
        try:
            key, cert, additional_certs = pkcs12.load_key_and_certificates(raw, password)
            break
        except Exception:
            continue
    else:
        raise ValueError(
            "PFX protegido por senha. Remova a senha antes de converter."
        )

    if target_format == "pem":
        pem_parts = []
        if cert:
            pem_parts.append(cert.public_bytes(serialization.Encoding.PEM).decode())
        if key:
            pem_parts.append(
                key.private_bytes(
                    serialization.Encoding.PEM,
                    serialization.PrivateFormat.TraditionalOpenSSL,
                    serialization.NoEncryption(),
                ).decode()
            )
        for c in (additional_certs or []):
            pem_parts.append(c.public_bytes(serialization.Encoding.PEM).decode())
        Path(output_path).write_text("\n".join(pem_parts), encoding="utf-8")

    else:
        raise ValueError(f"PFX não suporta saída: {target_format}")
