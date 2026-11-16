# Environment setup

A summary of how the lab was built, enough to reproduce it. Replace `<PC_IP>` and
`<VM_IP>` with the real addresses on your network.

## 1. Windows PC — prepare Docker

1. Docker Desktop with the WSL2 backend (`wsl -l -v` should show `docker-desktop` on
   version 2).
2. WSL2 memory in `%UserProfile%\.wslconfig`:
   ```ini
   [wsl2]
   memory=10GB
   ```
   Then `wsl --shutdown` and reopen Docker Desktop.
3. Set `vm.max_map_count` (required by the indexer / OpenSearch):
   ```powershell
   wsl -d docker-desktop sysctl -w vm.max_map_count=262144
   ```
4. Note the Ethernet adapter's IPv4 (`ipconfig`) = `<PC_IP>`; preferably reserve it on
   the router.

## 2. Windows PC — bring up Wazuh

```powershell
cd <project folder>
git clone -c core.autocrlf=false https://github.com/wazuh/wazuh-docker.git -b <stable version>
cd wazuh-docker\single-node
docker compose -f generate-indexer-certs.yml run --rm generator
docker compose up -d
```

Open `https://localhost` (default credentials in `docker-compose.yml`) and change the
passwords through the official procedure. **Do not version certificates or passwords.**

## 3. Linux laptop — victim VM

```bash
sudo apt install qemu-kvm libvirt-daemon-system virtinst virt-manager
sudo usermod -aG libvirt $USER
```

VM via `virt-manager`: Ubuntu Server LTS, 2 GB RAM, 2 vCPUs, 20 GB disk (qcow2), NAT
network (`default`), with OpenSSH. Update and take a clean snapshot.

## 4. Agent and connection

1. On the PC, open the ports in the firewall (PowerShell as admin):
   ```powershell
   New-NetFirewallRule -DisplayName "Wazuh agent (lab)" -Direction Inbound -Protocol TCP -LocalPort 1514,1515 -Action Allow -Profile Private
   ```
2. In the dashboard: Deploy new agent → Linux DEB amd64 → **Server address = `<PC_IP>`**.
3. Run the generated command on the VM and enable the `wazuh-agent` service.
4. Confirm `vitima01` as Active in the dashboard.

Step-by-step details, checkpoints, and puzzles for each stage are in the project's
walkthrough guide.
