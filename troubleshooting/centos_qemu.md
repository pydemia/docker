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


[root@accmaster ~]# yum install -y grubby
Loaded plugins: fastestmirror, product-id, search-disabled-repos, subscription-manager

This system is not registered with an entitlement server. You can use subscription-manager to register.

Loading mirror speeds from cached hostfile
epel/x86_64/metalink                                             |  19 kB  00:00:00
 * base: mirror.kakao.com
 * centos-sclo-rh: mirror.kakao.com
 * centos-sclo-sclo: mirror.kakao.com
 * epel: d2lzkl7pfhq30w.cloudfront.net
 * extras: mirror.kakao.com
 * updates: mirror.kakao.com
base                                                             | 3.6 kB  00:00:00
centos-sclo-rh                                                   | 3.0 kB  00:00:00
centos-sclo-sclo                                                 | 3.0 kB  00:00:00
docker-ce-stable                                                 | 3.5 kB  00:00:00
epel                                                             | 4.7 kB  00:00:00
extras                                                           | 2.9 kB  00:00:00
google-cloud-sdk/signature                                       |  454 B  00:00:00
google-cloud-sdk/signature                                       | 1.4 kB  00:00:00 !!!
nodesource                                                       | 2.5 kB  00:00:00
pgdg-common                                                      | 2.9 kB  00:00:00
pgdg10                                                           | 3.6 kB  00:00:00
pgdg11                                                           | 3.6 kB  00:00:00
pgdg12                                                           | 3.6 kB  00:00:00
pgdg95                                                           | 3.6 kB  00:00:00
pgdg96                                                           | 3.6 kB  00:00:00
updates                                                          | 2.9 kB  00:00:00
(1/9): epel/x86_64/updateinfo                                    | 1.0 MB  00:00:00
(2/9): epel/x86_64/primary_db                                    | 6.9 MB  00:00:00
(3/9): google-cloud-sdk/primary                                  | 124 kB  00:00:00
(4/9): pgdg10/7/x86_64/primary_db                                | 268 kB  00:00:01
(5/9): pgdg-common/7/x86_64/primary_db                           | 136 kB  00:00:01
(6/9): pgdg96/7/x86_64/primary_db                                | 258 kB  00:00:00
(7/9): pgdg11/7/x86_64/primary_db                                | 275 kB  00:00:02
(8/9): pgdg12/7/x86_64/primary_db                                | 142 kB  00:00:02
(9/9): pgdg95/7/x86_64/primary_db                                | 226 kB  00:00:02
google-cloud-sdk                                                                827/827
Package grubby-8.28-26.el7.x86_64 already installed and latest version
Nothing to do


[root@accmaster ~]# grubby --update-kernel=ALL --args="systemd.unified_cgroup_hierarchy=0"
error opening /boot/grub/grub.cfg for read: No such file or directory
```


---
```bash
$ vim /etc/default/grub

GRUB_CMDLINE_LINUX="systemd.unified_cgroup_hierarchy=0"
```


