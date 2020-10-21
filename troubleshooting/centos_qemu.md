# CentOS(7) on QEMU

```ascii
[root@accmaster system]# systemctl restart docker.service
Job for docker.service failed because the control process exited with error code. See "systemctl status docker.service" and "journalctl -xe" for details.
[root@accmaster system]# systemctl status docker.service
● docker.service - Docker Application Container Engine
   Loaded: loaded (/usr/lib/systemd/system/docker.service; enabled; vendor preset: disabled)
   Active: failed (Result: start-limit) since Tue 2020-10-20 15:15:01 KST; 51s ago
     Docs: https://docs.docker.com
  Process: 12617 ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock (code=exited, status=1/FAILURE)
 Main PID: 12617 (code=exited, status=1/FAILURE)

Oct 20 15:14:59 accmaster systemd[1]: Failed to start Docker Application Container Engine.
Oct 20 15:14:59 accmaster systemd[1]: Unit docker.service entered failed state.
Oct 20 15:14:59 accmaster systemd[1]: docker.service failed.
Oct 20 15:15:01 accmaster systemd[1]: docker.service holdoff time over, scheduling restart.
Oct 20 15:15:01 accmaster systemd[1]: Stopped Docker Application Container Engine.
Oct 20 15:15:01 accmaster systemd[1]: start request repeated too quickly for docker.service
Oct 20 15:15:01 accmaster systemd[1]: Failed to start Docker Application Container Engine.
Oct 20 15:15:01 accmaster systemd[1]: Unit docker.service entered failed state.
Oct 20 15:15:01 accmaster systemd[1]: docker.service failed.
[root@accmaster ~]# dockerd --debug
INFO[2020-10-20T15:20:32.112261461+09:00] Starting up
DEBU[2020-10-20T15:20:32.113474021+09:00] Listener created for HTTP on unix (/var/run/docker.sock)
DEBU[2020-10-20T15:20:32.114368580+09:00] Golang's threads limit set to 231390
INFO[2020-10-20T15:20:32.114738006+09:00] parsed scheme: "unix"                         module=grpc
INFO[2020-10-20T15:20:32.114754361+09:00] scheme "unix" not registered, fallback to default scheme  module=grpc
INFO[2020-10-20T15:20:32.114777154+09:00] ccResolverWrapper: sending update to cc: {[{unix:///run/containerd/containerd.sock 0  <nil>}] <nil>}  module=grpc
INFO[2020-10-20T15:20:32.114791616+09:00] ClientConn switching balancer to "pick_first"  module=grpc
INFO[2020-10-20T15:20:32.117065041+09:00] parsed scheme: "unix"                         module=grpc
INFO[2020-10-20T15:20:32.117083615+09:00] scheme "unix" not registered, fallback to default scheme  module=grpc
INFO[2020-10-20T15:20:32.117099467+09:00] ccResolverWrapper: sending update to cc: {[{unix:///run/containerd/containerd.sock 0  <nil>}] <nil>}  module=grpc
INFO[2020-10-20T15:20:32.117108680+09:00] ClientConn switching balancer to "pick_first"  module=grpc
DEBU[2020-10-20T15:20:32.117853442+09:00] Using default logging driver json-file
DEBU[2020-10-20T15:20:32.117873648+09:00] [graphdriver] trying provided driver: overlay2
DEBU[2020-10-20T15:20:32.117894896+09:00] processing event stream                       module=libcontainerd namespace=plugins.moby
DEBU[2020-10-20T15:20:32.132258164+09:00] backingFs=xfs, projectQuotaSupported=false, indexOff="index=off,"  storage-driver=overlay2
DEBU[2020-10-20T15:20:32.132296891+09:00] Initialized graph driver overlay2
WARN[2020-10-20T15:20:32.150433181+09:00] Your kernel does not support cgroup memory limit
WARN[2020-10-20T15:20:32.150451451+09:00] Unable to find cpu cgroup in mounts
WARN[2020-10-20T15:20:32.150459207+09:00] Unable to find blkio cgroup in mounts
WARN[2020-10-20T15:20:32.150465998+09:00] Unable to find cpuset cgroup in mounts
WARN[2020-10-20T15:20:32.150472548+09:00] mountpoint for pids not found
DEBU[2020-10-20T15:20:32.150688340+09:00] Cleaning up old mountid : start.
failed to start daemon: Devices cgroup isn't mounted
```
