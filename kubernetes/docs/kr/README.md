# Kubernetes

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
    * [**Nodes**]()
      * Master(~**Control Planes**)
      * Worker

  * Resources
    * **Namespaces**
    * [**Pods**(~Containers)]()
      * Pod as App
      * Sidecar Containers
    * Controllers
      * **Replicaset**: Pod 수를 안정적으로 유지
      * **Deployments**
      * StatefulSets
      * DaemonSet
      * **Jobs**
      * [**Services**: Pod로 구성된 APP을, IP 단위로 노출]()

  * Networking
    * **Proxy**(`kube-proxy`)
    * **CNI**: Container(Pod) Network Interface(L3 or L2 Overlay Network)
    * [**LoadBalancing**: Service를 클러스터 외부에 제공]()

  * Storage

  * Security
    * PrivateIP in VPC
    * **SSL**
    * **TLS** for Ingress (& **gRPC**)
    * **RBAC**(Role Based Access Control)
    * Encryption
    * Policy
      * PodSecurityPolicy


  * **Logging**

  * **Monitoring**

---


