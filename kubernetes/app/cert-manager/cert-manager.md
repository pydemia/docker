# Cert-Manager

<https://cert-manager.io/docs/installation/kubernetes/>

```bash
# Kubernetes 1.15+, Download first
$ wget https://github.com/jetstack/cert-manager/releases/download/v0.14.3/cert-manager.yaml -O
cert-manager.yaml

# Deploy it as guided
$ kubectl apply --validate=false -f cert-manager.yaml
```

**Note**: If you are running `Kubernetes v1.15.4 or below`, you will need to add the `--validate=false` flag to your kubectl apply command above else you will receive a validation error relating to the `x-kubernetes-preserve-unknown-fields` field in cert-manager’s `CustomResourceDefinition` resources. This is a benign error and occurs due to the way `kubectl` performs resource validation.
