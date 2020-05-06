# SSH Tunneling

## Use-case

* Connect to the `kubernetes-dashboard` remotely

If you need to access the Dashboard remotely, you can use SSH tunneling to do port forwarding from your localhost to the node running the `kubectl proxy` service. 
The easiest option is to use SSH tunneling to forward a port on your local system to the port configured for the `kubectl proxy` service on the node that you want to access. This method retains some security as the HTTP connection is encrypted by virtue of the SSH tunnel and authentication is handled by your SSH configuration. For example, on your local system run:

```bash
> ssh -L 8001:127.0.0.1:8001 <HOST IP ADDR-where the `kubectl proxy` is running>
```

or

```bash
> ssh -L 9999:127.0.0.1:8001 -N <username>@<kubernetes-dashboard-host>
```

When the SSH connection is established, you can open a browser on your `localhost` and navigate to:

```
http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/
```

Use **the same token info** to authenticate as if you were connecting to the dashboard locally.

```bash
> kubectl describe secret -n kubernetes-dashboard
```