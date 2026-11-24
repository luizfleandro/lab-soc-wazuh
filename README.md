# SOC Lab with Wazuh — Attack Detection and AI-Assisted Triage

A home SOC/DFIR lab built as a cybersecurity portfolio project. I simulate harmless
attacks on a monitored VM, check what the Wazuh SIEM detects, and measure, against a
ground-truth sheet, whether an AI can safely help a Tier-1 analyst triage the alerts,
including when an attacker tries to manipulate it through prompt injection.

**Full results:** [`docs/results.md`](docs/results.md)

## Key findings

- **Detection is the first bottleneck:** of 6 malicious scenarios, Wazuh (default
  rules) raised alerts for only 3. No triage layer can recover the other 3.
- **A naive rule (`rule.level >= 10`) caught 1 of those 3 scenarios;** the AI caught 2
  with confidence and flagged the third as inconclusive.
- **The AI never labelled a real attack as a false positive.** That supports a safe
  closing policy: the AI may auto-close only what it calls a false positive, and
  everything else goes to a human. On this dataset: **36% fewer alerts in the queue,
  no attacks missed**, at US$ 0.05 for 130 alerts.
- **Prompt injection:** no payload turned an attack into a false positive, including
  a real end-to-end SSH attack. Direct commands were recognised; a plausible
  explanation (renaming a malicious account to `ansible`) was more effective.
- **The attacker can choose a parsed SIEM field:** with a multi-word SSH username,
  the Wazuh decoder stored only the last word in `srcuser`.

## Architecture

| Machine | Role | Components |
| --- | --- | --- |
| PC (Windows, 16 GB, wired) | SOC server | Docker Desktop + WSL2 running Wazuh (manager, indexer, dashboard); triage scripts |
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
- **Python** for the triage pipeline: alert labelling, evaluation, and LLM calls
- **Claude Haiku 5.5** via the Anthropic API, with **Pydantic** to validate the
  JSON verdict

## Scenarios tested

Nine scenarios: one SSH brute force used to validate the pipeline, five malicious
Atomic Red Team tests, and three legitimate admin activities. The full list, with
times, techniques, whether Wazuh raised an alert, and which rules fired, is in
[`scenarios/ground_truth.csv`](scenarios/ground_truth.csv).

## Repository structure

| Path | Contents |
| --- | --- |
| [`docs/results.md`](docs/results.md) | Methodology, confusion matrices, closing policy, prompt injection tests, limitations |
| [`docs/installation.md`](docs/installation.md) | How the lab was built |
| [`docs/troubleshooting.md`](docs/troubleshooting.md) | Real errors encountered and how they were solved |
| [`docs/journal.md`](docs/journal.md) | Chronological lab journal |
| [`scenarios/ground_truth.csv`](scenarios/ground_truth.csv) | Ground truth of the scenarios |
| [`triage/`](triage/) | Triage pipeline, evaluation scripts, injection tests, and cached AI verdicts (`cache/v1/`) |

The cached verdicts allow anyone to reproduce the evaluation without an API key
(see "How to reproduce" in [`docs/results.md`](docs/results.md)).

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
- The clock of the investigated host cannot be trusted blindly: reverting a VM
  snapshot set its clock back by up to 35 minutes, so scenarios were matched using
  the manager's timestamp.
- AI output must always be validated, and invalid output escalated, never dropped:
  responses were truncated once by hidden reasoning tokens and malformed once.

## Limitations

- Single-node environment, no high availability, lab only.
- A single monitored endpoint (Linux).
- Small sample: one day of data, 37 alerts in scope, only 7 legitimate.
- The AI judges one alert at a time, without context.
- Lab artefacts (hostnames, the libvirt gateway IP, revealing account names) leaked
  into some AI verdicts.

> **Note:** no sensitive data (passwords, API keys, certificates, real IPs) is
> versioned in this repository.
