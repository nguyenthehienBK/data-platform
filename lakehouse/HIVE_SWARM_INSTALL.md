# Hive Metastore HA — Docker Swarm Installation Guide

Deploy 3 Hive Metastore instances across 3 servers using Docker Swarm for high availability.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Swarm Cluster                    │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Server 1   │  │   Server 2   │  │   Server 3   │       │
│  │  (Manager)   │  │  (Worker)    │  │  (Worker)    │       │
│  │              │  │              │  │              │       │
│  │  HMS-1       │  │  HMS-2       │  │  HMS-3       │       │
│  │  :19083      │  │  :29083      │  │  :39083      │       │
│  │              │  │              │  │              │       │
│  │  PostgreSQL  │  │              │  │              │       │
│  │  :5432       │  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                             │
│  Ingress routing mesh: any port reachable from any node     │
└─────────────────────────────────────────────────────────────┘
```

**Port mapping:**

| Instance | Internal Port | Published Port | Placement Label |
|---|---|---|---|
| HMS 1 | 9083 | 19083 | `hms=1` |
| HMS 2 | 9083 | 29083 | `hms=2` |
| HMS 3 | 9083 | 39083 | `hms=3` |
| PostgreSQL | 5432 | — | `node.role == manager` |

## Prerequisites

- 3 servers with Docker installed, reachable over network
- Network connectivity between all 3 servers (ports 2377, 7946, 4789 open)
- Docker images already pulled on all 3 servers:
  - `apachehudi/hive:latest`
  - `postgres:16`

## Step 1: Disable `live-restore` on all 3 servers

Docker Swarm is incompatible with `live-restore`. Disable it on **every server**.

```bash
sudo nano /etc/docker/daemon.json
```

Set or add:

```json
{
  "live-restore": false
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

> **Why:** `live-restore` keeps containers alive when the daemon stops. Swarm needs full control over container lifecycle for scheduling and reconciliation. Keeping both enabled would cause state divergence.

## Step 2: Initialize the Swarm (on Server 1)

On the **manager** node:

```bash
docker swarm init --advertise-addr <SERVER_1_IP>
```

This outputs a join token:

```
docker swarm join --token SWMTKN-xxx <SERVER_1_IP>:2377
```

Save this token — you'll need it for the workers.

## Step 3: Join workers to the Swarm (on Server 2 and Server 3)

On **Server 2** and **Server 3**, run the join command from Step 2:

```bash
docker swarm join --token SWMTKN-xxx <SERVER_1_IP>:2377
```

Verify on the manager:

```bash
docker node ls
```

Expected output (3 nodes, 1 manager, 2 workers):

```
ID              HOSTNAME    STATUS   AVAILABILITY   MANAGER STATUS
abc123 *        server-1    Ready    Active         Leader
def456          server-2    Ready    Active
ghi789          server-3    Ready    Active
```

## Step 4: Label each node (on Server 1)

Labels determine where each HMS instance is placed.

On the **manager** node:

```bash
docker node update --label-add hms=1 <SERVER_1_HOSTNAME>
docker node update --label-add hms=2 <SERVER_2_HOSTNAME>
docker node update --label-add hms=3 <SERVER_3_HOSTNAME>
```

Get hostnames from `docker node ls`.

Verify labels:

```bash
docker node inspect <HOSTNAME> --format '{{.Spec.Labels}}'
```

## Step 5: Create the overlay network (on Server 1)

```bash
docker network create --driver overlay --attachable hudi-datalake
```

- `--driver overlay`: enables cross-node communication in Swarm
- `--attachable`: allows standalone containers to also connect

## Step 6: Copy files to the manager node

Only the **manager** needs the files. Workers receive everything via Swarm.

Copy to the same directory on Server 1:

```
your-folder/
├── docker-compose.hms.yml
└── conf/
    └── hive/
        └── metastore-site.xml
```

Create the data directory for PostgreSQL:

```bash
mkdir -p ./data/hive-metastore-db
```

> **Note:** Swarm configs (`metastore-site.xml`) are stored in the Swarm raft store and automatically distributed to nodes. Workers never need local copies.

## Step 7: Deploy the stack (on Server 1)

```bash
docker stack deploy --resolve-image never -c docker-compose.hms.yml hms
```

`--resolve-image never` prevents Swarm from pulling images — uses local images only.

## Step 8: Verify

Check services:

```bash
docker service ls
```

Expected output:

```
NAME                  MODE         REPLICAS   IMAGE
hms_hive-metastore-1  replicated   1/1        apachehudi/hive:latest
hms_hive-metastore-2  replicated   1/1        apachehudi/hive:latest
hms_hive-metastore-3  replicated   1/1        apachehudi/hive:latest
hms_hive-metastore-db replicated   1/1        postgres:16
```

Wait until all show `1/1`. First deploy may take time for HMS to initialize the database schema.

Check which node each task is running on:

```bash
docker service ps hms_hive-metastore-1
docker service ps hms_hive-metastore-2
docker service ps hms_hive-metastore-3
```

Check logs:

```bash
docker service logs hms_hive-metastore-1
docker service logs hms_hive-metastore-2
docker service logs hms_hive-metastore-3
```

Test connectivity:

```bash
# From any machine on the network
telnet <SERVER_1_IP> 19083
telnet <SERVER_2_IP> 29083
telnet <SERVER_3_IP> 39083
```

> **Ingress routing mesh:** Published ports are accessible from **any** node in the cluster. Swarm routes traffic to the correct container automatically. So `telnet <SERVER_2_IP> 19083` also works — it routes to Server 1 where HMS-1 runs.

## Step 9: Connect from Spark / Trino

Update your client configuration to use all 3 HMS instances for failover:

**`spark-defaults.conf`:**

```properties
spark.hadoop.hive.metastore.uris=thrift://<SERVER_1_IP>:19083,thrift://<SERVER_2_IP>:29083,thrift://<SERVER_3_IP>:39083
```

**Trino `hudi.properties`:**

```properties
hive.metastore.uri=thrift://<SERVER_1_IP>:19083,thrift://<SERVER_2_IP>:29083,thrift://<SERVER_3_IP>:39083
```

Clients will try each URI in order and failover automatically.

## Common Operations

### Re-deploy after changes

```bash
docker stack deploy --resolve-image never -c docker-compose.hms.yml hms
```

Swarm applies only the changes (rolling update).

### Update `metastore-site.xml`

Swarm configs are immutable. To update:

```bash
# Option A: remove and recreate (causes brief downtime)
docker stack rm hms
docker config rm hms_metastore-site.xml
docker stack deploy --resolve-image never -c docker-compose.hms.yml hms

# Option B: rename the config in docker-compose.hms.yml, then just redeploy (zero downtime)
# 1. Edit compose: rename config to metastore-site-v2.xml
# 2. docker stack deploy --resolve-image never -c docker-compose.hms.yml hms
# 3. docker config rm hms_metastore-site.xml  (cleanup old one)
```

### Remove the stack

```bash
docker stack rm hms
```

### View service details

```bash
docker service inspect hms_hive-metastore-1
```

### View port mappings

```bash
docker service inspect hms_hive-metastore-1 --format '{{json .Endpoint.Ports}}'
```

## Troubleshooting

| Problem | Fix |
|---|---|
| Task keeps restarting | `docker service logs hms_hive-metastore-N` — usually DB not ready yet, wait and retry |
| Can't reach HMS from outside | Check firewall allows ports 19083, 29083, 39083 |
| Config changes not picked up | Configs are immutable — see "Update metastore-site.xml" above |
| `hms` label not found | Re-check `docker node update --label-add hms=N <HOSTNAME>` on manager |
| Image not found on worker | Pre-pull images on all nodes, or remove `--resolve-image never` |
| Swarm init fails with `live-restore` error | Disable `live-restore` in `/etc/docker/daemon.json` and restart Docker |
| `docker ps` shows 9083 not 19083 | Normal — Swarm routing mesh handles port mapping. Use `docker service ls` instead |

## Firewall Requirements

Open these ports on all 3 servers:

| Port | Protocol | Purpose |
|---|---|---|
| 2377 | TCP | Swarm management |
| 7946 | TCP+UDP | Node discovery |
| 4789 | UDP | Overlay network traffic |
| 19083 | TCP | HMS-1 |
| 29083 | TCP | HMS-2 |
| 39083 | TCP | HMS-3 |
