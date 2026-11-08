from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from sign_windows import sign


class SigningTests(unittest.TestCase):
    def test_required_identity_cannot_silently_produce_unsigned_release(self):
        with patch("sign_windows.subprocess.run") as run:
            with self.assertRaises(ValueError):
                sign("example.exe", required=True)
            run.assert_not_called()
            self.assertEqual(sign("example.exe"), "unsigned")

    def test_signing_requests_sha256_timestamp_and_verifies_trust(self):
        with patch("sign_windows.subprocess.run") as run:
            sign("example.exe", tool="signtool.exe", thumbprint="A" * 40, required=True)
            self.assertEqual(run.call_count, 2)
            args = run.call_args_list[0].args[0]
            self.assertIn("/tr", args)
            self.assertEqual(args[args.index("/fd") + 1], "SHA256")
            self.assertEqual(args[args.index("/td") + 1], "SHA256")
            self.assertEqual(run.call_args_list[1].args[0][1:4], ["verify", "/pa", "/all"])

    def test_verification_failure_stops_the_build(self):
        with patch("sign_windows.subprocess.run", side_effect=[None, subprocess.CalledProcessError(1, "verify")]):
            with self.assertRaises(subprocess.CalledProcessError):
                sign("example.exe", tool="signtool.exe", thumbprint="A" * 40, required=True)
