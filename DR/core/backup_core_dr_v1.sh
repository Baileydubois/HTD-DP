#!/usr/bin/env bash
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: backup_core_dr_v1.sh must run as root." >&2
  exit 1
fi

TS=$(date +%Y%m%d_%H%M%S)
BASE=/home/hydrotech/htd_backups
DIR=$BASE/dr_v1_core_$TS

install -d -o hydrotech -g hydrotech "$DIR"

echo '[1/7] HTD application archive'
tar -czf "$DIR/opt_htd.tar.gz" \
  --exclude='/opt/htd/backups' \
  --exclude='/opt/htd/data' \
  /opt/htd

echo '[2/7] Recoverable HTD data archive'
DATA_OK=0
for ATTEMPT in 1 2 3; do
  rm -f "$DIR/data_recovery.tar.gz"
  if tar -czf "$DIR/data_recovery.tar.gz" \
    /opt/htd/data/edges \
    /opt/htd/data/events/outbox \
    /opt/htd/data/events/deadletter \
    /opt/htd/data/export \
    /opt/htd/data/upload/queue \
    /opt/htd/data/upload/deadletter
  then
    DATA_OK=1
    break
  fi
  echo "Recoverable data changed during capture; retry $ATTEMPT/3" >&2
  sleep 2
done

if [ "$DATA_OK" -ne 1 ]; then
  echo "ERROR: unable to capture recoverable HTD data consistently." >&2
  exit 1
fi

echo '[3/7] System configuration archive'
tar -czf "$DIR/system_config.tar.gz" \
  /etc/htd \
  /etc/nginx \
  /etc/mosquitto \
  /etc/netplan \
  /etc/systemd/system/htd-*.service \
  /etc/systemd/system/htd-*.timer

echo '[4/7] Identity and storage inventory'
{
  echo '=== HOSTNAME ==='
  hostname
  echo '=== OS ==='
  cat /etc/os-release
  echo '=== KERNEL ==='
  uname -a
  echo '=== USER ==='
  id hydrotech
  echo '=== DISKS ==='
  lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS,UUID
  echo '=== FSTAB ==='
  cat /etc/fstab
} > "$DIR/identity_storage.txt"

echo '[5/7] Package and service inventory'
dpkg-query -W -f='${binary:Package}\t${Version}\n' > "$DIR/packages.txt"
systemctl list-unit-files 'htd-*' --no-pager > "$DIR/htd_units.txt"
crontab -u hydrotech -l > "$DIR/crontab_hydrotech.txt" 2>/dev/null || true

echo '[6/7] SHA256 manifest'
cd "$DIR"
sha256sum \
  crontab_hydrotech.txt \
  data_recovery.tar.gz \
  htd_units.txt \
  identity_storage.txt \
  opt_htd.tar.gz \
  packages.txt \
  system_config.tar.gz \
  > manifest.sha256

echo '[7/7] Verify manifest'
sha256sum -c manifest.sha256

chown hydrotech:hydrotech \
  crontab_hydrotech.txt \
  data_recovery.tar.gz \
  htd_units.txt \
  identity_storage.txt \
  opt_htd.tar.gz \
  packages.txt \
  system_config.tar.gz \
  manifest.sha256

echo
echo "DR_V1_CORE_OK=$DIR"
