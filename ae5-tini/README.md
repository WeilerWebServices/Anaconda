# Zombie killer for AE5 <= 5.4.1

This repository implements a hotfix that implements zombie process
collection for AE5 sessions, jobs, and deployments. When successfully
completed, the [`tini`](https://github.com/krallin/tini) binary is
inserted into PID 1, and all other processes become children of `tini`.
This process ensures full signal propagation and zombie collection.

Installation should introduce minimal disruption to a running cluster,
and can easily be reversed if needed:

1. Copy the contents of this repository to `/opt/anaconda/tini` on the master node.
2. Enter the Gravity environment and move to this directory.
3. Run `download_tini.sh` to download a `tini` binary. This scripts
   grabs a valid version of the binary and verifies its signature. If
   for any reason this fails—for instance, if your firewall blocks
   access—you can manually download the `tini` binary from this link:
   https://github.com/krallin/tini/releases/download/v0.19.0/tini
4. Run `install_tini.sh`. This will build new docker images for both
   sessions and deployments/jobs, push them to the internal registry,
   and modify the `workspace` and `deploy` deployments to use them.
   This will cause these deployments to restart, which will interrupt
   session and job/deployment operations for approximately 1 minute.
   However, existing sessions and deployments/jobs will not be disturbed.

If you wish to revert these changes, run `remove_tini.sh`. This will
revert the changes to the `workspace` and `deploy` deployments to point
to the stock images. As with step 4 above, this will interrupt operations
on sessions, jobs, and deployments for approximately 1 minute.

Both `install_tini.sh` and `remove_tini.sh` can be run multiple times
in succession without problems; the deployments will not be interrupted
if no change is required.

