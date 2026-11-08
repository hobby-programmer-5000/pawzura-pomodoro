"""Sign using an existing Windows certificate; never handle a private-key file."""
import re
import subprocess


def sign(executable, *, tool=None, thumbprint=None, required=False):
    if not thumbprint:
        if required:
            raise ValueError("A trusted signing identity is required before release")
        return "unsigned"
    thumbprint = thumbprint.replace(" ", "")
    if not tool or not re.fullmatch(r"[0-9a-fA-F]{40}", thumbprint):
        raise ValueError("Provide SignTool and the selected certificate's SHA1 thumbprint")
    subprocess.run([str(tool), "sign", "/s", "My", "/sha1", thumbprint, "/fd", "SHA256",
                    "/tr", "http://timestamp.digicert.com", "/td", "SHA256", str(executable)], check=True)
    subprocess.run([str(tool), "verify", "/pa", "/all", "/tw", str(executable)], check=True)
    return "authenticode verified with timestamp request"
