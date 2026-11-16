# Lab journal

A chronological log of what was done, what went wrong, and what I learned. Written
during the work, not at the end.

## 2026-11-15 — Planning

- Defined the project: a SOC/DFIR lab with Wazuh and, later, AI-assisted alert triage.
- Defined the architecture: Wazuh in Docker on the Windows PC (16 GB); victim VM in
  KVM on the Linux laptop (6 GB). Reason for the split: the single-node SIEM needs at
  least 8 GB, which the laptop lacks; and separating the SIEM from the victim mirrors
  a real deployment.

## 2026-11-16 — Setup and first round of tests

**Environment**

- Brought up Wazuh single-node in Docker; dashboard reachable at `https://localhost`.
- Created an Ubuntu Server VM in KVM, NAT network, with the Wazuh agent.
- Connected the agent to the manager (see problems 1 and 2 in `docs/troubleshooting.md`).
- VM registered in the dashboard as `vitima01`, status Active. CPU AMD Ryzen 5 3500U,
  2 vCPUs, ~3.3 GB of RAM assigned.

**Pipeline validation**

- SSH brute-force test (several wrong passwords). **Detected**: the dashboard showed
  the MITRE tactics Credential Access and Lateral Movement, and PCI DSS requirement
  10.2.4 (invalid access attempts). Also confirmed the raw alert in
  `/var/ossec/logs/alerts/alerts.json` inside the manager container.
- Usage lesson: alerts appear in Threat Hunting → Events, not only in the summary; and
  the time range must be short for the spike to be visible.

**First round of scenarios (Atomic Red Team)**

Run one by one, with the time recorded and cleanup/snapshot between rounds. Times and
techniques in `scenarios/ground_truth.csv`. From now on, the habit of reading each
test's YAML/MD before running it (description, input_arguments, executor, cleanup).

- 10:31 — T1136.001 create local account (`useradd` with system-account options).
- 10:42 — T1053.003 cron persistence (harmless script every minute).
- 10:45 — T1087.001 local account enumeration.
- 10:55 — T1070.003 clear command history.
- 11:11 — T1105 file download via `curl` from a homemade attacker host
  (`python3 -m http.server` on the laptop). See problem 5.
- 11:14 — L01 (legitimate) `apt update && upgrade`.
- 11:15 — L02 (legitimate) `sudo systemctl restart` of a service.
- 11:15 — L03 (legitimate) a single wrong SSH password.

**Pending**

- Fill in the detection result of each scenario in the ground-truth sheet (did it
  raise an alert? rule and level) based on what Wazuh showed.
- Analyze the gaps: malicious scenarios that raised no alert.
- Compare the `sudo` alert from L02 with the one from the malicious account-creation
  scenario: what tells them apart beyond the command text?
