"""
Customer Directory MCP — Hardening Demo
========================================
A minimal MCP server demonstrating output-field filtering as a defense
against sensitive data leakage through tool outputs.

Toggle ENABLE_OUTPUT_FILTERING to see vulnerable vs hardened behavior.

Maps to Hardening Guide:
  - Section 5 (Secrets Management): least-privilege scope on data exposure
  - Section 8 (Policy & Guardrails): runtime filtering of tool outputs
  - Section 4 (Traffic Mediation): would normally enforce this at gateway level

All data is mock and in-memory. No filesystem writes, no persistence,
no external calls. Process exits = data gone.
"""

import sys
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("customer-directory-hardened")

# ═══════════════════════════════════════════════════════════════════
# HARDENING TOGGLE
# ═══════════════════════════════════════════════════════════════════
# False = vulnerable (full records including SSN, credit card returned)
# True  = hardened  (output filtered to safe fields only)

ENABLE_OUTPUT_FILTERING = True

# Fields safe for LLM consumption. Everything else is stripped when the
# toggle is True. To add a field to LLM-visible output, add it here.
ALLOWED_FIELDS = {"customer_id", "name", "email", "account_type", "city"}

# ═══════════════════════════════════════════════════════════════════
# MOCK DATA
# ═══════════════════════════════════════════════════════════════════

CUSTOMERS = {
    "C-1042": {
        "customer_id": "C-1042",
        "name": "Alex Tremblay",
        "email": "alex.tremblay@example.com",
        "account_type": "Platinum",
        "city": "Toronto",
        # SENSITIVE — must never reach the LLM in production
        "ssn": "123-45-6789",
        "credit_card": "4567-1234-5678-9012",
        "internal_fraud_notes": "Flagged for manual review 2026-03-15 — possible card-testing pattern",
    },
    "C-2087": {
        "customer_id": "C-2087",
        "name": "Priya Sharma",
        "email": "priya.sharma@example.com",
        "account_type": "Gold",
        "city": "Vancouver",
        "ssn": "987-65-4321",
        "credit_card": "5678-2345-6789-0123",
        "internal_fraud_notes": "No flags — clean account since 2019",
    },
    "C-3104": {
        "customer_id": "C-3104",
        "name": "Marcus Chen",
        "email": "marcus.chen@example.com",
        "account_type": "Centurion",
        "city": "Montreal",
        "ssn": "456-78-9012",
        "credit_card": "3782-822463-10005",
        "internal_fraud_notes": "VIP — senior approval required for account changes",
    },
}

# ═══════════════════════════════════════════════════════════════════
# TOOLS
# ═══════════════════════════════════════════════════════════════════

@mcp.tool()
def list_customers() -> list[dict]:
    """List all customer IDs with their names. Use this to find customer
    IDs before calling get_customer_info."""
    return [
        {"customer_id": cid, "name": rec["name"]}
        for cid, rec in CUSTOMERS.items()
    ]


@mcp.tool()
def get_customer_info(customer_id: str) -> dict:
    """Retrieve a customer's profile information by their customer ID.
    Returns the customer's account details."""

    if customer_id not in CUSTOMERS:
        return {"error": f"Customer {customer_id} not found"}

    record = CUSTOMERS[customer_id].copy()
    original_count = len(record)

    # ───────────────────────────────────────────────────────────────
    # HARDENING BLOCK — comment out the next 3 lines (or set the
    # toggle to False) to see SSN, credit_card, and fraud notes leak
    # ───────────────────────────────────────────────────────────────
    if ENABLE_OUTPUT_FILTERING:
        record = {k: v for k, v in record.items() if k in ALLOWED_FIELDS}
        sys.stderr.write(
            f"[HARDENING] get_customer_info({customer_id}): "
            f"returned {len(record)}/{original_count} fields "
            f"(blocked {original_count - len(record)} sensitive fields)\n"
        )
    else:
        sys.stderr.write(
            f"[VULNERABLE] get_customer_info({customer_id}): "
            f"returning full record with {original_count} fields "
            f"including SSN and credit card\n"
        )

    return record


if __name__ == "__main__":
    mcp.run()