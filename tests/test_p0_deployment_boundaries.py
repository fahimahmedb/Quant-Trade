"""Astra Phase-7 durability falsification tests.

Synthetic bytes only. These tests cover publication durability boundaries that
can affect whether a raw object is legitimately acknowledged after a crash.
"""
from __future__ import annotations

import errno
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from quant.paths import QuantPaths
from quant.dataplane.sec.store import SecCaptureStore, SecStorageFailure, digest_bytes

ROOT = Path(__file__).resolve().parents[1]


class RawPublicationDurabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.paths = QuantPaths(Path(self.temp.name))
        self.store = SecCaptureStore(self.paths, root=ROOT)

    def test_retry_after_directory_fsync_failure_revalidates_durability(self) -> None:
        """A visible hardlink after failed fsync is not yet durable evidence."""
        body = b"synthetic-p0-raw-object"
        object_id = digest_bytes(body)
        target = self.store.object_path(object_id)

        with mock.patch.object(
            self.store,
            "_fsync_dir",
            side_effect=OSError(errno.EIO, "synthetic directory fsync failure"),
        ):
            with self.assertRaises(SecStorageFailure):
                self.store.put_object(body)

        self.assertTrue(
            target.exists(),
            "the adversarial boundary requires the link to exist after fsync failed",
        )

        original = SecCaptureStore._fsync_dir
        with mock.patch.object(
            self.store,
            "_fsync_dir",
            wraps=lambda path: original(path),
        ) as fsync_dir:
            result = self.store.put_object(body)

        self.assertTrue(result.deduplicated)
        touched = [call.args[0] for call in fsync_dir.call_args_list]
        self.assertIn(
            target.parent,
            touched,
            "retry must durably revalidate the directory containing the object",
        )
        self.assertIn(
            target.parent.parent,
            touched,
            "retry must also durably revalidate the hash-prefix directory entry",
        )

    def test_new_hash_prefix_is_fsynced_in_its_parent(self) -> None:
        """Creating <raw>/<prefix>/ must itself be durable before ACK."""
        body = b"synthetic-new-prefix"
        target = self.store.object_path(digest_bytes(body))

        with mock.patch.object(self.store, "_fsync_dir") as fsync_dir:
            self.store.put_object(body)

        touched = [call.args[0] for call in fsync_dir.call_args_list]
        self.assertIn(target.parent, touched)
        self.assertIn(
            target.parent.parent,
            touched,
            "fsync(prefix) does not by itself make creation of prefix durable in raw/",
        )


if __name__ == "__main__":
    unittest.main()
