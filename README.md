# SOC Lab with Wazuh — Attack Detection and AI-Assisted Triage

A home SOC/DFIR lab built as a cybersecurity portfolio project. I simulate harmless
attacks on a monitored VM, check what the Wazuh SIEM detects, and document the
detection gaps. The next phase adds an AI layer that triages the alerts and is
measured against a ground-truth sheet.

## Goal

Prove, end to end, the path of a security event — from the action on the machine to
the alert in the SIEM — and use it as the basis to test, with numbers, whether an AI
can reliably triage the alerts of a Tier-1 SOC analyst.

## Architecture

| Machine | Role | Components |
| --- | --- | --- |
| PC (Windows, 16 GB, wired) | SOC server | Docker Desktop + WSL2 running Wazuh (manager, indexer, dashboard) |
| Laptop (Linux, 6 GB, Wi-Fi) | Victim host / attacker | KVM with the victim VM; source of the tests |
| Victim VM (Ubuntu Server) | Monitored endpoint | Wazuh agent; where the attacks run |

The VM agent initiates the connection to the manager on the PC over TCP ports 1514
and 1515. The VM sits on a KVM NAT network (`192.168.122.0/24`), so only the PC's
firewall needs to be opened. The lab uses two physical machines on purpose:
separating the SIEM from the monitored host mirrors a real deployment and prevents a
compromise of the victim from affecting monitoring.

## Tools

- **Wazuh** (open-source SIEM) via Docker, single-node deployment
- **KVM / libvirt** for the victim VM, with snapshots
- **Atomic Red Team** as the source of attack scenarios, mapped to MITRE ATT&CK
- **Python** (`http.server`) as the attacker host for the download scenario

## Scenarios tested

Eight scenarios in a first round: five malicious and three legitimate. The full list
with timestamps and techniques is in [`scenarios/ground_truth.csv`](scenarios/ground_truth.csv).
The SSH brute force, used to validate the pipeline, was confirmed detected
(Credential Access tactic and PCI DSS requirement 10.2.4 in the dashboard). The
detection result for the remaining scenarios is under analysis and will be filled in
the ground-truth sheet.

## What I learned

- Tracing an alert's path layer by layer (action → log → agent → manager →
  dashboard) to find where an event is lost.
- Diagnosing connectivity by elimination: an `nc`/`ping` that hangs with no response
  points to a silently dropped packet (firewall or service down), unlike an
  immediate refusal.
- The difference between monitoring *executed commands* and *files on disk* explains
  why some actions (such as a `curl` download) may not raise an alert.
- Routine administrator actions and attacker actions can produce the **same** kind of
  alert (use of `sudo`), which defines the core problem of triage.

## Limitations

- Single-node environment, no high availability, lab only.
- A single monitored endpoint (Linux).
- Low event volume; does not reflect the load of a real SOC.

## Next steps (AI phase)

A Python script that reads the manager's `alerts.json`, asks an AI for a verdict in a
fixed JSON schema (incident / false positive / inconclusive), compares the verdict
against the ground truth, builds a confusion matrix, and tests prompt injection
through the SSH username field.

> **Note:** no sensitive data (passwords, certificates, real IPs) is versioned in
> this repository. See [`docs/troubleshooting.md`](docs/troubleshooting.md) for the
> log of real errors encountered and how they were solved.
