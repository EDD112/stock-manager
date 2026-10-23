"""
Custom HTTPS development server that works with Python 3.12+/3.14.
Usage: python manage.py runsecure
       python manage.py runsecure 0.0.0.0:8443
"""
import os
import ssl
import sys
import subprocess
import threading
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.core.servers.basehttp import WSGIServer, WSGIRequestHandler, run
from django.core.wsgi import get_wsgi_application

CERT_FILE = "cert.pem"
KEY_FILE = "key.pem"


def generate_cert():
    """Generate self-signed cert. Tries openssl CLI first, then cryptography lib."""
    if os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE):
        return True

    # Method 1: openssl command
    try:
        subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", KEY_FILE, "-out", CERT_FILE,
            "-days", "365", "-nodes",
            "-subj", "/CN=localhost",
        ], check=True, capture_output=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass

    # Method 2: cryptography library
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "localhost")])
        cert = (
            x509.CertificateBuilder()
            .subject_name(name)
            .issuer_name(name)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365))
            .sign(key, hashes.SHA256())
        )
        with open(KEY_FILE, "wb") as f:
            f.write(key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption(),
            ))
        with open(CERT_FILE, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        return True
    except ImportError:
        pass

    return False


class SecureWSGIServer(WSGIServer):
    """WSGIServer wrapped with TLS."""
    def __init__(self, address, handler_cls, cert_file, key_file):
        super().__init__(address, handler_cls)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(cert_file, key_file)
        self.socket = ctx.wrap_socket(self.socket, server_side=True)


class Command(BaseCommand):
    help = "Run Django dev server with HTTPS (works on Python 3.12+/3.14)"

    def add_arguments(self, parser):
        parser.add_argument(
            "addrport", nargs="?", default="0.0.0.0:8443",
            help="Address:port to bind (default: 0.0.0.0:8443)",
        )

    def handle(self, *args, **options):
        addrport = options["addrport"]
        if ":" in addrport:
            addr, port = addrport.rsplit(":", 1)
            port = int(port)
        else:
            addr, port = "0.0.0.0", int(addrport)

        if not generate_cert():
            self.stderr.write(
                self.style.ERROR(
                    "Cannot generate SSL certificate.\n"
                    "Install OpenSSL or run: pip install cryptography"
                )
            )
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS(f"[✓] SSL certificate ready: {CERT_FILE}"))

        application = get_wsgi_application()

        server = SecureWSGIServer((addr, port), WSGIRequestHandler, CERT_FILE, KEY_FILE)
        server.set_app(application)

        self.stdout.write(self.style.SUCCESS(f"[✓] HTTPS server running at https://{addr}:{port}/"))
        self.stdout.write(f"    Open on your phone: https://<your-pc-ip>:{port}/")
        self.stdout.write(f"    (Tap 'Advanced' > 'Proceed' to bypass the certificate warning)")
        self.stdout.write(f"    Press Ctrl+C to stop.\n")

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            self.stdout.write("\n[*] Server stopped.")
            server.server_close()
