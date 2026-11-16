# Problems encountered and how I solved them

A log of the lab's real errors. For each one: the symptom, how I investigated it, the
root cause, and what I learned. This is the part of the project that shows
troubleshooting reasoning.

## 1. Agent would not connect — Docker was closed

- **Symptom:** from the VM, `nc -zv <PC_IP> 1515` and `ping` to the PC hung, with no
  response and no error.
- **Investigation:** I tested layer by layer (IP, route, firewall). The `nc` hanging,
  instead of "connection refused", pointed to a silently dropped packet.
- **Root cause:** Docker Desktop was closed on the PC, so no Wazuh container was up to
  listen on the ports.
- **Fix:** start Docker Desktop. To prevent recurrence, I enabled auto-start and
  confirmed the containers have a restart policy.
- **Lesson:** a service that failed to come up after a reboot is a common cause of a
  "hung connection" in production too. Hang ≠ refuse: the difference already tells you
  whether the problem is a firewall/service or a closed port.

## 2. Agent pointing at the wrong IP

- **Symptom:** in the VM's `ossec.log`, repeated errors
  `(1208): Unable to connect to enrollment service at '[192.168.122.75]:1515'`.
- **Investigation:** I read the agent log and noticed the destination address was the
  VM's own IP, in the NAT range `192.168.122.x`.
- **Root cause:** in the "Deploy new agent" wizard, the VM's IP was entered as the
  "Server address" instead of the IP of the PC running Wazuh.
- **Fix:** correct the `<address>` field inside `<client><server>` in the VM's
  `/var/ossec/etc/ossec.conf` to the PC's IP, and restart the agent.
- **Lesson:** reading the log and finding the line that explains the failure is an
  analyst's daily work. The wrong address was written in the error itself.

## 3. Forgotten Wazuh dashboard password

- **Symptom:** I could not remember the username/password to log into the dashboard.
- **Root cause:** default credentials live in `docker-compose.yml`; after the change,
  the new ones apply.
- **Fix:** locate `INDEXER_USERNAME`/`INDEXER_PASSWORD` in the compose file; when
  needed, redo the official password-change procedure. In a lab with no data, one
  option is to recreate the stack with `docker compose down -v`.
- **Lesson:** store the password in a password manager and never version the compose
  file with real passwords.

## 4. "no crontab for ubuntu"

- **Symptom:** the message "no crontab for ubuntu" when checking the crontab.
- **Root cause:** not an error; it just means the user did not have a crontab yet.
- **Fix:** understand that the test command creates/replaces the crontab; confirm
  afterwards with `crontab -l`.
- **Lesson:** not every message is an error. Reading carefully avoids "fixing" what is
  not broken.

## 5. T1105 download did not reach the host

- **Symptom:** `curl` from the VM to the laptop's HTTP server timed out; the Python
  server logged no request.
- **Investigation:** no log on the server = the packet never arrived. I tested a ping
  to the NAT gateway and the laptop's firewall.
- **Root cause:** a combination of the file being served from the wrong folder, using
  the home-network IP instead of the laptop's IP on the NAT network
  (`192.168.122.1`), and the laptop's firewall.
- **Fix:** start `python3 -m http.server` in the file's folder, use the IP
  `192.168.122.1`, and open the port in the firewall for the lab range.
- **Lesson:** the VM reaches the laptop through its address on the NAT network, which
  is the gateway `192.168.122.1`, not through the home-network IP.

## 6. Alerts "missing" in the dashboard

- **Symptom:** after a test, the agent summary showed no alerts.
- **Root cause:** the summary screen shows counts and charts, not the list. Also, the
  time range was set to "Last 24 hours", so the spike of events became a nearly
  invisible dot.
- **Fix:** use Threat Hunting → Events with a short range (15 min / 1 h) and a filter
  by `agent.name`.
- **Lesson:** knowing where each piece of information appears in the SIEM is half the
  job of a Tier-1 analyst in the first weeks.
