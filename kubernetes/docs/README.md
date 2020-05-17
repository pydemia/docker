# Kubernetes


<https://kubernetes.io/docs/concepts>

---
## Table of Contents

* Docker
  * [**Images & Containers**]()
    * Runtimes
  * [**Networking**]()
  * [**Storage**]()
    * [Volume]()

* Kubernetes
  * Structure
    * Cluster
    * [**Nodes**](): VM
      * Master: a node has **Control Planes**
      * Worker: a normal node

  * Resources
    * **Namespace**
    * [**Pod**(~Container)]()
      * Pod as App
      * Sidecar Container
    * Controllers
      * **Replicaset**: to maintain Pods with replication
        * label selector: a filter to select Pods by given labels.
      * **Deployment**: to deploy APPs, by defining Pods and ReplicaSets
        * StatefulSet: a Deployment to manage stateful APPs
        * DaemonSet: a Deployment to deploy Pods on the selected Nodes, without moving through Nodes. (for Node logging or monitoring, etc.)
      * **Jobs**
    * ConfigMap: to store config data with `KEY-VALUE` pairs; env-vars or arguments, etc.

  * Networking
    * **Proxy**(`kube-proxy`)
    * **CNI**: Container(Pod) Network Interface(L3 or L2 Overlay Network)
    * [**LoadBalancing**](): to Expose Services

  * [**Exposing**](exposing/README.md)
    * [**Service**](): An Abstract way to expose APPs, running on a set of Pods.
      * `ClusterIP`: within Cluster
      * `NodePort`: rely on Node, if Node(VM) IP is accessible
      * `LoadBalancer`: by given (IP, DomainName) in Cloud
      * `ExternalName`: bygiven DNS name
      * `Headless`: Service without `ClusterIP`
    * [**Ingress**](): L7 with LoadBalancer


  * Storage
    * Volume
      * CSI(Container Storage Interface)
    * PV(PersistentVolume)
    * PVC(PersistentVolumeClaim): a request for storage by a user. similar to a Pod, PVC consumes PV resources.

  * Security
    * Pod Security
      * ServiceAccount
      * Secret, ConfigMap for `confidential data`
        * TLS
    * PrivateIP in VPC
    * **SSL**
    * **TLS** for Ingress (& **gRPC**)
    * **RBAC**(Role Based Access Control)
    * Encryption
    * Policy
      * PodSecurityPolicy

  * Scheduling

  * **Logging**

  * **Monitoring**

---

* Node: A worker machine in Kubernetes, part of a cluster.
* Cluster: A set of Nodes that run containerized applications managed by Kubernetes. For this example, and in most common Kubernetes deployments, nodes in the cluster are not part of the public internet.
* Edge router: A router that enforces the firewall policy for your cluster. This could be a gateway managed by a cloud provider or a physical piece of hardware.
* Cluster network: A set of links, logical or physical, that facilitate communication within a cluster according to the Kubernetes networking model.
* Service: A Kubernetes Service that identifies a set of Pods using label selectors. Unless mentioned otherwise, Services are assumed to have virtual IPs only routable within the cluster network.


