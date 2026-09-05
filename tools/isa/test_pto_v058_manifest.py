#!/usr/bin/env python3
"""Regression tests for the PTO 0.58 manifest contract."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/isa"))

import check_pto_v058_manifest as checker  # noqa: E402


def load(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class ExtensionReservationCardinalityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.documents = {
            "meta": load("isa/v0.58/meta.json"),
            "release": load("isa/v0.58/release_manifest.json"),
            "lock": load("isa/v0.58/pto-spec.lock.json"),
            "reservations": load(
                "isa/v0.58/state/extension_encoding_reservations.json"
            ),
        }

    def validate(self, documents: dict[str, Any]) -> list[str]:
        return checker.validate_extension_reservation_cardinality(
            documents["meta"],
            documents["release"],
            documents["lock"],
            documents["reservations"],
        )

    def test_checked_in_cardinalities_agree(self) -> None:
        self.assertEqual(self.validate(self.documents), [])

    def test_exact_publication_lock_identity_is_enforced(self) -> None:
        self.assertEqual(checker.validate_lock_identity(self.documents["lock"]), [])
        mutations = {
            "catalog digest": lambda lock: lock["catalogs"]["command_forms"].__setitem__(
                "sha256", "0" * 64
            ),
            "source commit": lambda lock: lock["source"].__setitem__("commit", "0" * 40),
            "release manifest": lambda lock: lock["release_manifest"].__setitem__(
                "sha256", "0" * 64
            ),
            "numeric vectors": lambda lock: lock["numeric_conformance_vectors"].__setitem__(
                "sha256", "0" * 64
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                lock = copy.deepcopy(self.documents["lock"])
                mutate(lock)
                self.assertTrue(checker.validate_lock_identity(lock))

    def test_each_cross_file_cardinality_drift_is_rejected(self) -> None:
        mutations = {
            "meta": lambda docs: docs["meta"]["cardinality"].__setitem__(
                "extension_encoding_reservations", 45
            ),
            "release manifest": lambda docs: docs["release"]["cardinality"].__setitem__(
                "extension_encoding_reservations", 45
            ),
            "PTO lock": lambda docs: docs["lock"]["catalogs"][
                "extension_encoding_reservations"
            ].__setitem__("count", 45),
            "reservation projection": lambda docs: docs["reservations"].__setitem__(
                "reservation_count", 39
            ),
            "reservation inventory": lambda docs: docs["reservations"][
                "reservations"
            ].pop(),
        }
        for source, mutate in mutations.items():
            with self.subTest(source=source):
                documents = copy.deepcopy(self.documents)
                mutate(documents)
                errors = self.validate(documents)
                self.assertTrue(
                    any(
                        "extension reservation cardinalities must agree at 46" in error
                        for error in errors
                    ),
                    errors,
                )

    def test_metadata_narrative_drift_is_rejected(self) -> None:
        documents = copy.deepcopy(self.documents)
        documents["meta"]["notes"] = [
            note.replace("46 extension reservations", "32 extension reservations")
            for note in documents["meta"]["notes"]
        ]
        errors = self.validate(documents)
        self.assertTrue(
            any("metadata notes must state" in error for error in errors), errors
        )

    def test_null_and_wrong_type_structures_are_rejected_without_exceptions(self) -> None:
        mutations = {
            "metadata cardinality null": (
                lambda docs: docs["meta"].__setitem__("cardinality", None),
                "v0.58 metadata cardinality must be a JSON object",
            ),
            "release cardinality list": (
                lambda docs: docs["release"].__setitem__("cardinality", []),
                "v0.58 release manifest cardinality must be a JSON object",
            ),
            "lock catalogs null": (
                lambda docs: docs["lock"].__setitem__("catalogs", None),
                "v0.58 PTO lock catalogs must be a JSON object",
            ),
            "lock reservation catalog list": (
                lambda docs: docs["lock"]["catalogs"].__setitem__(
                    "extension_encoding_reservations", []
                ),
                "v0.58 PTO lock extension reservation catalog must be a JSON object",
            ),
            "reservation projection list": (
                lambda docs: docs.__setitem__("reservations", []),
                "v0.58 extension reservation projection must be a JSON object",
            ),
            "reservation inventory object": (
                lambda docs: docs["reservations"].__setitem__("reservations", {}),
                "v0.58 extension reservation inventory must be a JSON array",
            ),
            "metadata notes null": (
                lambda docs: docs["meta"].__setitem__("notes", None),
                "v0.58 metadata notes must be a JSON array of strings",
            ),
            "metadata note object": (
                lambda docs: docs["meta"].__setitem__("notes", [{}]),
                "v0.58 metadata notes must be a JSON array of strings",
            ),
        }
        for structure, (mutate, expected_error) in mutations.items():
            with self.subTest(structure=structure):
                documents = copy.deepcopy(self.documents)
                mutate(documents)
                self.assertIn(expected_error, self.validate(documents))

    def test_missing_cross_file_fields_are_rejected(self) -> None:
        mutations = {
            "meta cardinality": lambda docs: docs["meta"].pop("cardinality"),
            "release cardinality": lambda docs: docs["release"].pop("cardinality"),
            "lock catalogs": lambda docs: docs["lock"].pop("catalogs"),
            "reservation count": lambda docs: docs["reservations"].pop(
                "reservation_count"
            ),
            "reservation inventory": lambda docs: docs["reservations"].pop(
                "reservations"
            ),
            "metadata notes": lambda docs: docs["meta"].pop("notes"),
        }
        for field, mutate in mutations.items():
            with self.subTest(field=field):
                documents = copy.deepcopy(self.documents)
                mutate(documents)
                errors = self.validate(documents)
                self.assertTrue(errors, f"missing {field} was accepted")


if __name__ == "__main__":
    unittest.main()
