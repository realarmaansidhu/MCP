# Customer Directory MCP — Hardening Demo

A minimal MCP server demonstrating output-field filtering as a defense
against sensitive data leakage through tool outputs.

## What this demonstrates

Even when an LLM is asked — legitimately or via prompt injection — to
"return all info about customer X," a properly hardened MCP only returns
fields explicitly approved for LLM consumption. SSN, credit card numbers,
and internal fraud notes never leave the MCP server. They can't be leaked
because the LLM never receives them.

This is the **least-privilege output scope** principle from Hardening
Sections 5 and 8 applied at the tool-implementation layer.

## The toggle

In `customer_directory.py`:

    ENABLE_OUTPUT_FILTERING = True   # Hardened
    ENABLE_OUTPUT_FILTERING = False  # Vulnerable

That's the entire defense. Flip the boolean to see the difference.

## Demo flow

### Run 1 — Vulnerable

1. Set `ENABLE_OUTPUT_FILTERING = False`
2. Connect this MCP to your agent
3. Ask: *"Get me everything you know about customer C-1042"*
4. Observe: full record returned, including SSN, credit card, fraud notes
5. Stderr: `[VULNERABLE] ... returning full record with 8 fields...`

### Run 2 — Hardened

1. Set `ENABLE_OUTPUT_FILTERING = True`
2. Same prompt
3. Observe: only customer_id, name, email, account_type, city returned
4. Stderr: `[HARDENING] ... blocked 3 sensitive fields`

The LLM cannot leak what it never received.

## What this does NOT cover (and why)

This demo stays beginner-friendly and laptop-runnable. A production
hardening of this same MCP would also include:

- **Runtime isolation** (Section 3): Docker container, non-root user,
  read-only filesystem, egress filtering
- **Traffic mediation** (Section 4): API gateway with rate limiting,
  request logging, response inspection
- **Secrets management** (Section 5): vault-fetched short-lived
  credentials instead of hardcoded mock data
- **Observability** (Section 6): structured logging with request IDs,
  centralized to SIEM
- **Policy engine** (Section 8): OPA/Cedar evaluating each call against
  declarative policy ("only authenticated reviewers can see
  internal_fraud_notes")
- **Audit trails**: every access logged with caller identity for
  compliance review

The toggle in this file demonstrates one principle clearly. Production
composes many such principles together.

## TTP categories this defends against

- **Cat 3 (Data Exfiltration)**: SSN and credit card can't be
  exfiltrated if they never reach the LLM
- **Cat 1 (Prompt Injection)**: even a successful injection can't
  extract data the MCP refuses to expose
- **Cat 9 (Excessive Tool Permissions)**: the tool's own output is
  scoped to minimum necessary fields