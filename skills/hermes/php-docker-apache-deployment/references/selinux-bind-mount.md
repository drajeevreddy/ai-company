# SELinux Bind Mount Details

## The Problem
On Fedora/RHEL with SELinux Enforcing (`getenforce = Enforcing`), Docker bind mounts from the host into containers are blocked by default because the container process (running in a different SELinux context) cannot read/write the host files.

## The Solution: `:z` Flag
```bash
docker run -v /host/path:/container/path:z ...
```
The `:z` flag tells Docker to relabel the host directory with a shared SELinux label (`container_file_t` with a shared MCS label) so the container can access it.

## Alternative: `:Z` (Private)
- `:z` = shared (multiple containers can access)
- `:Z` = private (only this container)
Use `:z` for our case since we only have one container.

## Verification
```bash
# On host
ls -Z /home/user/app
# Should show container_file_t with s0:cXXX,cYYY labels

# In container
ls -Z /var/www/html
# Same labels
```

## Common Errors Without `:z`
- 403 Forbidden (Apache can't read files)
- 500 Internal Server Error (Apache can't write to data/ config/ logs/)
- Permission denied in PHP logs

## Fedora-Specific Notes
- Default policy is targeted, Enforcing
- `setenforce 0` works temporarily but is NOT a solution (security regression)
- Persistent: edit `/etc/selinux/config` but requires reboot
- `:z` is the correct production approach