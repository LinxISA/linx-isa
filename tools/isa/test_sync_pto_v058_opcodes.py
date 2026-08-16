#!/usr/bin/env python3
"""Behavioral tests for PTO opcode ownership migration."""

import unittest

import sync_pto_v058_opcodes as sync


def instruction(form_id: str, match: str) -> dict:
    return {
        "pto_source_form_id": form_id,
        "encoding": {
            "parts": [
                {
                    "mask": "0xffffffff",
                    "match": match,
                    "width_bits": 32,
                }
            ]
        },
    }


class OpcodeOwnershipMigrationTest(unittest.TestCase):
    def test_singleton_field_constraint_is_folded_into_fixed_encoding(self) -> None:
        form = {
            "asm": "BSTART.STD FALL",
            "constraints": [
                {"field": "simm17", "operator": "one-of", "values": [0]}
            ],
            "encoding": [
                {
                    "index": 0,
                    "mask": "0x00007fff",
                    "match": "0x00001001",
                    "width_bits": 32,
                }
            ],
            "fields": [
                {
                    "name": "simm17",
                    "width": 17,
                    "pieces": [
                        {
                            "instruction_lsb": 15,
                            "value_lsb": 0,
                            "width": 17,
                        }
                    ],
                }
            ],
            "form_id": "bstart_std_fall",
            "length_bits": 32,
            "mnemonic": "BSTART.STD",
            "semantic_group": "Bundle Split",
            "semantic_summary": "Start a standard fall-through block.",
        }

        line = sync.opcode_line(form, form["encoding"], None, {})

        assignments, operands, _ = line.split(" : ", 1)[1].split(" ; ")
        self.assertIn("31..0=32'b00000000000000000001000000000001", assignments)
        self.assertNotIn("simm17", assignments)
        self.assertEqual(operands, "")
        self.assertIn(
            '"pto_source_fixed_fields":[{"name":"simm17","value":0,"width":17}]',
            line,
        )

    def test_scalar_rows_are_replaced_from_the_new_catalog(self) -> None:
        action = sync.classify_owned_instruction(
            instruction("scalar-form", "0x00000001"),
            scalar_form_ids={"scalar-form"},
            command_form_ids=set(),
            reservations=[],
        )
        self.assertEqual(action, "replace")

    def test_removed_reserved_command_becomes_linx_owned(self) -> None:
        action = sync.classify_owned_instruction(
            instruction("linx-extension", "0x00000002"),
            scalar_form_ids=set(),
            command_form_ids=set(),
            reservations=[
                {
                    "encoding": [
                        {
                            "mask": "0xffffffff",
                            "match": "0x00000002",
                            "width_bits": 32,
                        }
                    ]
                }
            ],
        )
        self.assertEqual(action, "preserve")

    def test_removed_unreserved_command_is_deleted(self) -> None:
        action = sync.classify_owned_instruction(
            instruction("obsolete-command", "0x00000003"),
            scalar_form_ids=set(),
            command_form_ids=set(),
            reservations=[],
        )
        self.assertEqual(action, "drop")


if __name__ == "__main__":
    unittest.main()
