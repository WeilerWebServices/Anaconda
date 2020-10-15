# A simple Prefect agent for AE5

This repository provides support for the creation of AE5 projcts to run Prefect flows and tasks. The goal is to allow Prefect flows to be run inside a standard AE5 deployment.

These files currently assume the use of Prefect Cloud. Future versions of this repo will provide support for local Prefect servers. Note however that whether using Prefect Cloud or a local server, all execution occurs on AE5 itself, and only logging and status information is delivered to Prefect Cloud. So Prefect's SaaS offering may be a viable option for many users even when working with sensitive data.

## Files
- `anaconda-project.yml`: the project specification. Currently, the package 
  list has exactly one dependency, `prefect`. Add any other packages you 
  need to implement your Flows to this list. Note however that Prefect does 
  require Python 3.6 or later.
- `endpoint/index.html`: this is a very simple static web page that is
  served on AE5's deployment endpoint. Because Prefect does not actually 
  utilize port 8086, AE5 would think this deployment is broken if the 
  Prefect agent were the only process that is running. To solve this problem 
  we run a very simple web server here to let AE5 know that we are alive. In 
  a future version, we could consider modifying this page to offer much more 
  useful content.
- `flows.py`: this is where the Prefect flows are instantiated. You can use
  as many Python files as you wish to implement your flows, but this script 
  needs to import them and register them with the Prefect server.
- `prefect_run.sh`: this is the script that the AE5 deployment runs. It does
  four things:
  1. Launches the background web server to keep the AE5 deployment healthy
  2. Authenticates with the Prefect server (currently assumes Prefect Cloud)
  3. Runs `flows.py` to create and register the flows
  4. Launches Prefect Agent to connect to the server for monitoring and
     notification

## Instructions
1. You need one USER token and one RUNNER token from Prefect Cloud.
   These will need to be stored as AE5 secrets. Specifically, go to your AE5 
   account settings screen (`/account/settings`) and add two secrets:
   - `prefectuser` for the USER token value
   - `prefectrunner` for the RUNNER token value.
2. Create a new project in AE5 and include these files. Note that the
   `endpoint` directory is essential; do not just include `index.html` into
   the root of your project.
3. Develop your flows. The `prefect_run.sh` script expects that `flows.py`
   will include a `flow.register` statement for each flow you wish to 
   include here. The flows should _not_ be run by the script (`flow.run`), 
   only registered.
4. Launch a terminal and run `prefect_run.sh`. This will authenticate to the
   server, register your flows, and launch a local agent. Head over to
   Prefect Cloud and confirm that the agent has successfully connected, and
   if you wish launch runs of each flow to confirm that they are operating 
   properly. Hit Ctrl-C to end the test.
5. When ready to move this to production, run this AE5 project _as a
   deployment_, not as a job. By launching it as a _deployment_, you can 
   rely on automatic restarts in case something goes wrong with the cluster. 
   The deployment can remain private, and it does not matter what its
   endpoint is. 
   
## TBD

There is a lot that can be done to improve this. Initial thoughts:
- Make better use of multicore AE5 deployments using local Dask execution
- Support connections to internally deployed Prefect UI servers.
- Do something interesting with the web endpoint—redirect to the appropriate
  status page on Prefect Server, provide a simple log viewer that allows the
  logs for the individual runs to be viewed; etc.
- Flesh out best practices for when to run multiple flows in the same
  versus running separate deployments. 
- Build a much more ambitious sample flow

