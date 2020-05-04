# Kubernetes Dashboard

[github-Kubernetes/dashboard](https://github.com/kubernetes/dashboard)

**_IMPORTANT_**: Read the [Access Control](https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/README.md) guide before performing any further steps.  
The default Dashboard deployment contains a minimal set of RBAC privileges needed to run.  

# Prerequisite

## Access Control

Check existing secrets in kubernetes-dashboard namespace.

```sh
# List it
kubectl -n kubernetes-dashboard get secret

# Get descriptions & token info
kubectl -n kubernetes-dashboard describe secrets <NAME>
```

### Create An Authentication Token (RBAC)

[Link](https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md)

In this guide, we will find out how to create a new user using Service Account mechanism of Kubernetes, grant this user admin permissions and login to Dashboard using bearer token tied to this user.

**IMPORTANT**: Make sure that you know what you are doing before proceeding. Granting admin privileges to Dashboard's Service Account might be a security risk.

For each of the following snippets for `ServiceAccount` and `ClusterRoleBinding`, you should copy them to new manifest files like `dashboard-adminuser.yaml` and use `kubectl apply -f dashboard-adminuser.yaml` to create them.

### Create a Service Account
* name: `admin-user` 
* namespace: `kubernetes-dashboard`

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kubernetes-dashboard
```

### Create ClusterRoleBinding

In most cases after provisioning our cluster using `kops` or `kubeadm` or any other popular tool, the `ClusterRole` `cluster-admin` already exists in the cluster. We can use it and create only `ClusterRoleBinding` for our `ServiceAccount`.

**NOTE:** `apiVersion` of `ClusterRoleBinding` resource may differ between Kubernetes versions. Prior to Kubernetes `v1.8` the `apiVersion` was `rbac.authorization.k8s.io/v1beta1`.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
```

## Bearer Token

Now we need to find token we can use to log in. Execute following command:

```bash
kubectl -n kubernetes-dashboard describe secret $(kubectl -n kubernetes-dashboard get secret | grep admin-user | awk '{print $1}')
```

It should print something like:

```ascii
Name:         admin-user-token-v57nw
Namespace:    kubernetes-dashboard
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: admin-user
              kubernetes.io/service-account.uid: 0303243c-4040-4a58-8a47-849ee9ba79c1

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1066 bytes
namespace:  20 bytes
token:      eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuLXY1N253Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIwMzAzMjQzYy00MDQwLTRhNTgtOGE0Ny04NDllZTliYTc5YzEiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6YWRtaW4tdXNlciJ9.Z2JrQlitASVwWbc-s6deLRFVk5DWD3P_vjUFXsqVSY10pbjFLG4njoZwh8p3tLxnX_VBsr7_6bwxhWSYChp9hwxznemD5x5HLtjb16kI9Z7yFWLtohzkTwuFbqmQaMoget_nYcQBUC5fDmBHRfFvNKePh_vSSb2h_aYXa8GV5AcfPQpY7r461itme1EXHQJqv-SN-zUnguDguCTjD80pFZ_CmnSE1z9QdMHPB8hoB4V68gtswR1VLa6mSYdgPwCHauuOobojALSaMc3RH7MmFUumAgguhqAkX3Omqd3rJbYOMRuMjhANqd08piDC3aIabINX6gP5-Tuuw2svnV6NYQ
```

Now copy the token and paste it into `Enter token` field on login screen.


## Access Control

### Service Account

* Create it:

```sh
# Alias Command
kubectl create sa <ACCOUNT NAME>

# Full Command
kubectl create serviceaccount <ACCOUNT NAME>
```

* Delete it:

```sh
kubectl delete sa <ACCOUNT NAME>
```

kubectl create sa kbmonitor -n kubernetes-dashboard

```bash
> kubectl create sa kubernetes-dashboard
serviceaccount/kubernetes-dashboard created

> kubectl get sa kubernetes-dashboard -o yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  creationTimestamp: "2020-05-04T06:45:29Z"
  name: kubernetes-dashboard
  namespace: default
  resourceVersion: "112658"
  selfLink: /api/v1/namespaces/default/serviceaccounts/kubernetes-dashboard
  uid: c88963ad-a95b-4bd9-88a2-dca2c927833f
secrets:
- name: kubernetes-dashboard-token-zb2vt
```

Get Bearer Token:
```sh
kubectl get secret $(kubectl get serviceaccount kubernetes-dashboard -o jsonpath="{.secrets[0].name}") -o jsonpath="{.data.token}" | base64 --decode
```


* Error:
```yaml
        args:
          - --auto-generate-certificates
```

Works as expected. Default `--auto-generate-certificates` flag generates self-signed certs that will not be recognized as **"safe"**. You can use your own certs if needed. It is described on our wiki.
[Link](https://github.com/kubernetes/dashboard/issues/3801)

```sh
# Generate private key and certificate signing request
> openssl genrsa -des3 -passout pass:over4chars -out dashboard.pass.key 2048
Generating RSA private key, 2048 bit long modulus (2 primes)
..+++++
........+++++
e is 65537 (0x010001)

> openssl rsa -passin pass:over4chars -in dashboard.pass.key -out dashboard.key
writing RSA key

> # rm dashboard.pass.key

> openssl req -new -key dashboard.key -out dashboard.csr
Can't load /home/pydemia/.rnd into RNG
548119844480:error:2406F079:random number generator:RAND_load_file:Cannot open file:../crypto/rand/randfile.c:88:Filename=/home/pydemia/.rnd
You are about to be asked to enter information that will be incorporated
into your certificate request.
What you are about to enter is what is called a Distinguished Name or a DN.
There are quite a few fields but you can leave some blank
For some fields there will be a default value,
If you enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:KR
State or Province Name (full name) [Some-State]:
Locality Name (eg, city) []:
Organization Name (eg, company) [Internet Widgits Pty Ltd]:
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:
Email Address []:

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:

# Generate SSL certificate
> openssl x509 -req -sha256 -days 365 -in dashboard.csr -signkey dashboard.key -out dashboard.crt
Signature ok
subject=C = KR, ST = Some-State, O = Internet Widgits Pty Ltd
Getting Private key
```

## Error:

### RND
```sh
sudo sed -i -e 's?^RANDFILE?#RANDFILE?g' /etc/ssl/openssl.cnf
```

### `csrf`

```ascii
kubectl logs -n kubernetes-dashboard kubernetes-dashboard-7f9fd5966c-gcz5z
2020/05/04 12:54:09 Starting overwatch
2020/05/04 12:54:09 Using namespace: kubernetes-dashboard
2020/05/04 12:54:09 Using in-cluster config to connect to apiserver
2020/05/04 12:54:09 Using secret token for csrf signing
2020/05/04 12:54:09 Initializing csrf token from kubernetes-dashboard-csrf secret
panic: Get https://10.96.0.1:443/api/v1/namespaces/kubernetes-dashboard/secrets/kubernetes-dashboard-csrf: dial tcp 10.96.0.1:443: i/o timeout

goroutine 1 [running]:
github.com/kubernetes/dashboard/src/app/backend/client/csrf.(*csrfTokenManager).init(0x40002889a0)
        /home/travis/build/kubernetes/dashboard/src/app/backend/client/csrf/manager.go:41 +0x38c
github.com/kubernetes/dashboard/src/app/backend/client/csrf.NewCsrfTokenManager(...)
        /home/travis/build/kubernetes/dashboard/src/app/backend/client/csrf/manager.go:66
github.com/kubernetes/dashboard/src/app/backend/client.(*clientManager).initCSRFKey(0x400016e080)
        /home/travis/build/kubernetes/dashboard/src/app/backend/client/manager.go:501 +0xb0
github.com/kubernetes/dashboard/src/app/backend/client.(*clientManager).init(0x400016e080)
        /home/travis/build/kubernetes/dashboard/src/app/backend/client/manager.go:469 +0x40
github.com/kubernetes/dashboard/src/app/backend/client.NewClientManager(...)
        /home/travis/build/kubernetes/dashboard/src/app/backend/client/manager.go:550
main.main()
        /home/travis/build/kubernetes/dashboard/src/app/backend/dashboard.go:105 +0x1dc
```

---

# Setup
* Deploy it:

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
```

or

```bash
wget https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml \
  -O kubernetes-dashboard-v2.0.0.yaml
kubectl apply -f kubernetes-dashboard-v2.0.0.yaml
```

kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/v1.6.0/src/deploy/kubernetes-dashboard.yaml


```bash
wget https://raw.githubusercontent.com/kubernetes/dashboard/v1.6.0/src/deploy/kubernetes-dashboard.yaml \
  -O kubernetes-dashboard-v1.6.0.yaml
kubectl apply -f kubernetes-dashboard-v1.6.0.yaml
```


```ascii
namespace/kubernetes-dashboard created
serviceaccount/kubernetes-dashboard created
service/kubernetes-dashboard created
secret/kubernetes-dashboard-certs created
secret/kubernetes-dashboard-csrf created
secret/kubernetes-dashboard-key-holder created
configmap/kubernetes-dashboard-settings created
role.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrole.rbac.authorization.k8s.io/kubernetes-dashboard created
rolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
deployment.apps/kubernetes-dashboard created
service/dashboard-metrics-scraper created
deployment.apps/dashboard-metrics-scraper created


NAMESPACE              NAME                                         READY   STATUS    RESTARTS   AGE
...
kubernetes-dashboard   dashboard-metrics-scraper-76679bc5b9-vd9rg   1/1     Running   0          21m
kubernetes-dashboard   kubernetes-dashboard-7f9fd5966c-g59xx        0/1     Error     8          21m
```

* Access it:

```bash
kubectl proxy

Starting to serve on 127.0.0.1:8001
```
 Now access dashboard at:
 <http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/>

If you want to access it from remote, will need to grant `ClusterRole` to allow access to dashboard.


```bash
kubectl get secret,sa,role,rolebinding,services,deployments --namespace=kubernetes-dashboard | grep das
hboard
```


* Stop it:

```bash
kubectl delete -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.0.0/aio/deploy/recommended.yaml
```


```bash
-o: allowed formats are: custom-columns,custom-columns-file,go-template,go-template-file,json,jsonpath,jsonpath-file,name,template,templatefile,wide,yaml
```

```bash
kubectl get pods -n kubernetes-dashboard -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'|grep kubernetes-dashboard
```

```bash
# Get Logs `kubernetes-dashboard-xxx-xx`
> kubectl logs -n kubernetes-dashboard $(kubectl get pods -n kubernetes-dashboard -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'|grep kubernetes-dashboard | awk '{print $1}')

> kubectl describe pods -n kubernetes-dashboard $(kubectl get pods -n kubernetes-dashboard -o go-template --template '{{range .items}}{{.metadata.name}}{{"\n"}}{{end}}'|grep kubernetes-dashboard | awk '{print $1}')
```