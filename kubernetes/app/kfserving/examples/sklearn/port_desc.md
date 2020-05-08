# Port, TargetPort, and NodePort in Kubernetes

## Pod port list

This array, defined in `pod.spec.containers[].ports`, provides a list of ports that get exposed by the container. You don’t really need to specify this list—even if it’s empty, as long as your containers are listening on the port, they’ll still be available for network access. This just provides some extra information to Kubernetes.

## Service ports list
The service’s `service.spec.ports` list configures which requests to a service port get forwarded to which ports on its pods. A successful request can be made from outside the cluster to the node’s IP address and service’s `nodePort`, forwarded to the service’s `port`, and received on the `targetPort` by the pod.

```yaml
kind: Service
apiVersion: v1
metadata:
  name: port-example-svc
spec:
  # Make the service externally visible via the node
  type: NodePort

  ports:
    # Which port on the node is the service available through?
    - nodePort: 31234

    # Inside the cluster, what port does the service expose?
    - port: 8080

    # Which port do pods selected by this service expose?
    - targetPort:

  selector:
    # ...
```

* `nodePort`
This setting makes the service visible outside the Kubernetes cluster by the node’s IP address and the port number declared in this property. The service also has to be of type NodePort (if this field isn’t specified, Kubernetes will allocate a node port automatically).

* `port`
Expose the service on the specified port internally within the cluster. That is, the service becomes visible on this port, and will send requests made to this port to the pods selected by the service.

* `targetPort`
This is the port on the pod that the request gets sent to. Your application needs to be listening for network requests on this port for the service to work.

From <https://matthewpalmer.net/kubernetes-app-developer/articles/kubernetes-ports-targetport-nodeport-service.html>