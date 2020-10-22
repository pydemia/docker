# Kubernetes Apps

## Upgrade

### Cert-Manager

Regular Process
https://cert-manager.io/docs/installation/upgrading/

* `0.14` to `0.15`
https://cert-manager.io/docs/installation/upgrading/upgrading-0.14-0.15/


### Istio

* `1.5` to `1.6`
https://istio.io/v1.6/docs/setup/upgrade/

** Upgrade from `1.4`
https://istio.io/v1.6/docs/setup/upgrade/#upgrading-from-1-4


### Knative

* `0.14` to `0.15`

https://knative.dev/v0.15-docs/install/upgrade-installation/

```bash
$ kubectl apply --filename https://github.com/knative/serving/releases/download/v0.15.0/serving-storage-version-migration.yaml
job.batch/storage-version-migration created


$ kubectl apply --filename https://github.com/knative/eventing/releases/download/v0.15.0/storage-version-migration-v0.15.0.yaml
clusterrole.rbac.authorization.k8s.io/knative-eventing-post-install-job-role created
serviceaccount/knative-eventing-post-install-job created
clusterrolebinding.rbac.authorization.k8s.io/knative-eventing-post-install-job-role-binding created
job.batch/storage-version-migration created


$ kubectl apply --filename https://github.com/knative/serving/releases/download/v0.15.0/serving.yaml \
> --filename https://github.com/knative/eventing/releases/download/v0.15.0/eventing.yaml \
> --filename https://github.com/knative/serving/releases/download/v0.15.0/monitoring.yaml
customresourcedefinition.apiextensions.k8s.io/images.caching.internal.knative.dev unchanged
namespace/knative-serving unchanged
serviceaccount/controller unchanged
clusterrole.rbac.authorization.k8s.io/knative-serving-admin configured
clusterrolebinding.rbac.authorization.k8s.io/knative-serving-controller-admin unchanged
image.caching.internal.knative.dev/queue-proxy unchanged
configmap/config-autoscaler unchanged
configmap/config-defaults unchanged
configmap/config-deployment unchanged
configmap/config-domain unchanged
configmap/config-gc unchanged
configmap/config-leader-election unchanged
configmap/config-logging unchanged
configmap/config-network unchanged
configmap/config-observability unchanged
configmap/config-tracing unchanged
horizontalpodautoscaler.autoscaling/activator unchanged
deployment.apps/activator configured
service/activator-service unchanged
deployment.apps/autoscaler unchanged
service/autoscaler unchanged
deployment.apps/controller configured
service/controller unchanged
deployment.apps/webhook unchanged
service/webhook unchanged
customresourcedefinition.apiextensions.k8s.io/certificates.networking.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/configurations.serving.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/ingresses.networking.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/metrics.autoscaling.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/podautoscalers.autoscaling.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/revisions.serving.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/routes.serving.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/serverlessservices.networking.internal.knative.dev unchanged
customresourcedefinition.apiextensions.k8s.io/services.serving.knative.dev unchanged
clusterrole.rbac.authorization.k8s.io/knative-serving-addressable-resolver unchanged
clusterrole.rbac.authorization.k8s.io/knative-serving-namespaced-admin unchanged
clusterrole.rbac.authorization.k8s.io/knative-serving-namespaced-edit unchanged
clusterrole.rbac.authorization.k8s.io/knative-serving-namespaced-view unchanged
clusterrole.rbac.authorization.k8s.io/knative-serving-core unchanged
clusterrole.rbac.authorization.k8s.io/knative-serving-podspecable-binding unchanged
validatingwebhookconfiguration.admissionregistration.k8s.io/config.webhook.serving.knative.dev unchanged
mutatingwebhookconfiguration.admissionregistration.k8s.io/webhook.serving.knative.dev unchanged
validatingwebhookconfiguration.admissionregistration.k8s.io/validation.webhook.serving.knative.dev unchanged
secret/webhook-certs unchanged
clusterrole.rbac.authorization.k8s.io/custom-metrics-server-resources configured
clusterrolebinding.rbac.authorization.k8s.io/custom-metrics:system:auth-delegator configured
clusterrolebinding.rbac.authorization.k8s.io/hpa-controller-custom-metrics configured
rolebinding.rbac.authorization.k8s.io/custom-metrics-auth-reader configured
deployment.apps/autoscaler-hpa created
service/autoscaler-hpa created
apiservice.apiregistration.k8s.io/v1beta1.custom.metrics.k8s.io configured
clusterrole.rbac.authorization.k8s.io/knative-serving-istio configured
gateway.networking.istio.io/knative-ingress-gateway configured
gateway.networking.istio.io/cluster-local-gateway configured
mutatingwebhookconfiguration.admissionregistration.k8s.io/webhook.istio.networking.internal.knative.dev configured
validatingwebhookconfiguration.admissionregistration.k8s.io/config.webhook.istio.networking.internal.knative.dev configured
secret/istio-webhook-certs configured
configmap/config-istio configured
deployment.apps/networking-istio configured
deployment.apps/istio-webhook configured
service/istio-webhook configured
namespace/knative-eventing configured
serviceaccount/eventing-controller configured
clusterrolebinding.rbac.authorization.k8s.io/eventing-controller configured
clusterrolebinding.rbac.authorization.k8s.io/eventing-controller-resolver configured
clusterrolebinding.rbac.authorization.k8s.io/eventing-controller-source-observer configured
clusterrolebinding.rbac.authorization.k8s.io/eventing-controller-sources-controller configured
clusterrolebinding.rbac.authorization.k8s.io/eventing-controller-manipulator configured
serviceaccount/pingsource-mt-adapter configured
clusterrolebinding.rbac.authorization.k8s.io/knative-eventing-pingsource-mt-adapter configured
serviceaccount/eventing-webhook configured
clusterrolebinding.rbac.authorization.k8s.io/eventing-webhook configured
clusterrolebinding.rbac.authorization.k8s.io/eventing-webhook-resolver configured
clusterrolebinding.rbac.authorization.k8s.io/eventing-webhook-podspecable-binding configured
configmap/config-br-default-channel configured
configmap/config-br-defaults configured
configmap/default-ch-webhook configured
configmap/config-leader-election configured
configmap/config-logging configured
configmap/config-observability configured
configmap/config-tracing configured
deployment.apps/eventing-controller configured
deployment.apps/eventing-webhook configured
service/eventing-webhook configured
customresourcedefinition.apiextensions.k8s.io/apiserversources.sources.knative.dev configured
customresourcedefinition.apiextensions.k8s.io/brokers.eventing.knative.dev configured
customresourcedefinition.apiextensions.k8s.io/channels.messaging.knative.dev configured
customresourcedefinition.apiextensions.k8s.io/containersources.sources.knative.dev configured
customresourcedefinition.apiextensions.k8s.io/eventtypes.eventing.knative.dev configured
customresourcedefinition.apiextensions.k8s.io/parallels.flows.knative.dev configured
customresourcedefinition.apiextensions.k8s.io/pingsources.sources.knative.dev configured
customresourcedefinition.apiextensions.k8s.io/sequences.flows.knative.dev configured
customresourcedefinition.apiextensions.k8s.io/sinkbindings.sources.knative.dev configured
customresourcedefinition.apiextensions.k8s.io/subscriptions.messaging.knative.dev configured
customresourcedefinition.apiextensions.k8s.io/triggers.eventing.knative.dev configured
clusterrole.rbac.authorization.k8s.io/addressable-resolver configured
clusterrole.rbac.authorization.k8s.io/service-addressable-resolver configured
clusterrole.rbac.authorization.k8s.io/serving-addressable-resolver configured
clusterrole.rbac.authorization.k8s.io/channel-addressable-resolver configured
clusterrole.rbac.authorization.k8s.io/broker-addressable-resolver configured
clusterrole.rbac.authorization.k8s.io/messaging-addressable-resolver configured
clusterrole.rbac.authorization.k8s.io/flows-addressable-resolver configured
clusterrole.rbac.authorization.k8s.io/eventing-broker-filter configured
clusterrole.rbac.authorization.k8s.io/eventing-broker-ingress configured
clusterrole.rbac.authorization.k8s.io/eventing-config-reader configured
clusterrole.rbac.authorization.k8s.io/channelable-manipulator configured
clusterrole.rbac.authorization.k8s.io/meta-channelable-manipulator configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-namespaced-admin configured
clusterrole.rbac.authorization.k8s.io/knative-messaging-namespaced-admin configured
clusterrole.rbac.authorization.k8s.io/knative-flows-namespaced-admin configured
clusterrole.rbac.authorization.k8s.io/knative-sources-namespaced-admin configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-namespaced-edit configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-namespaced-view configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-controller configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-pingsource-mt-adapter configured
clusterrole.rbac.authorization.k8s.io/podspecable-binding configured
clusterrole.rbac.authorization.k8s.io/builtin-podspecable-binding configured
clusterrole.rbac.authorization.k8s.io/source-observer configured
clusterrole.rbac.authorization.k8s.io/eventing-sources-source-observer configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-sources-controller configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-webhook configured
validatingwebhookconfiguration.admissionregistration.k8s.io/config.webhook.eventing.knative.dev configured
mutatingwebhookconfiguration.admissionregistration.k8s.io/webhook.eventing.knative.dev configured
validatingwebhookconfiguration.admissionregistration.k8s.io/validation.webhook.eventing.knative.dev configured
secret/eventing-webhook-certs configured
mutatingwebhookconfiguration.admissionregistration.k8s.io/sinkbindings.webhook.sources.knative.dev configured
clusterrolebinding.rbac.authorization.k8s.io/eventing-channel-broker-controller configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-channel-broker-controller configured
customresourcedefinition.apiextensions.k8s.io/configmappropagations.configs.internal.knative.dev configured
deployment.apps/broker-controller configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-mt-channel-broker-controller configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-mt-broker-filter configured
serviceaccount/mt-broker-filter configured
clusterrole.rbac.authorization.k8s.io/knative-eventing-mt-broker-ingress configured
serviceaccount/mt-broker-ingress configured
clusterrolebinding.rbac.authorization.k8s.io/eventing-mt-channel-broker-controller configured
clusterrolebinding.rbac.authorization.k8s.io/knative-eventing-mt-broker-filter configured
clusterrolebinding.rbac.authorization.k8s.io/knative-eventing-mt-broker-ingress configured
deployment.apps/broker-filter configured
service/broker-filter configured
deployment.apps/broker-ingress configured
service/broker-ingress configured
deployment.apps/mt-broker-controller configured
horizontalpodautoscaler.autoscaling/broker-ingress-hpa configured
horizontalpodautoscaler.autoscaling/broker-filter-hpa configured
configmap/config-imc-event-dispatcher configured
clusterrole.rbac.authorization.k8s.io/imc-addressable-resolver configured
clusterrole.rbac.authorization.k8s.io/imc-channelable-manipulator configured
clusterrole.rbac.authorization.k8s.io/imc-controller configured
clusterrole.rbac.authorization.k8s.io/imc-dispatcher configured
service/imc-dispatcher configured
serviceaccount/imc-dispatcher configured
serviceaccount/imc-controller configured
clusterrolebinding.rbac.authorization.k8s.io/imc-controller configured
clusterrolebinding.rbac.authorization.k8s.io/imc-dispatcher configured
customresourcedefinition.apiextensions.k8s.io/inmemorychannels.messaging.knative.dev created
deployment.apps/imc-controller configured
deployment.apps/imc-dispatcher configured
namespace/knative-monitoring unchanged
service/elasticsearch-logging created
serviceaccount/elasticsearch-logging created
clusterrole.rbac.authorization.k8s.io/elasticsearch-logging unchanged
clusterrolebinding.rbac.authorization.k8s.io/elasticsearch-logging configured
statefulset.apps/elasticsearch-logging created
service/kibana-logging created
deployment.apps/kibana-logging created
configmap/fluentd-ds-config created
serviceaccount/fluentd-ds created
clusterrole.rbac.authorization.k8s.io/fluentd-ds configured
clusterrolebinding.rbac.authorization.k8s.io/fluentd-ds configured
service/fluentd-ds created
daemonset.apps/fluentd-ds created
serviceaccount/kube-state-metrics unchanged
role.rbac.authorization.k8s.io/kube-state-metrics-resizer unchanged
rolebinding.rbac.authorization.k8s.io/kube-state-metrics unchanged
clusterrole.rbac.authorization.k8s.io/kube-state-metrics unchanged
clusterrolebinding.rbac.authorization.k8s.io/kube-state-metrics unchanged
deployment.apps/kube-state-metrics unchanged
service/kube-state-metrics unchanged
configmap/grafana-dashboard-definition-kubernetes-deployment unchanged
configmap/grafana-dashboard-definition-kubernetes-capacity-planning unchanged
configmap/grafana-dashboard-definition-kubernetes-cluster-health unchanged
configmap/grafana-dashboard-definition-kubernetes-cluster-status unchanged
configmap/grafana-dashboard-definition-kubernetes-control-plane-status unchanged
configmap/grafana-dashboard-definition-kubernetes-resource-requests unchanged
configmap/grafana-dashboard-definition-kubernetes-nodes unchanged
configmap/grafana-dashboard-definition-kubernetes-pods unchanged
configmap/grafana-dashboard-definition-kubernetes-statefulset unchanged
serviceaccount/node-exporter unchanged
clusterrole.rbac.authorization.k8s.io/node-exporter unchanged
clusterrolebinding.rbac.authorization.k8s.io/node-exporter unchanged
daemonset.apps/node-exporter unchanged
service/node-exporter unchanged
configmap/grafana-custom-config configured
configmap/grafana-dashboard-definition-knative-efficiency unchanged
configmap/grafana-dashboard-definition-knative-reconciler unchanged
configmap/scaling-config unchanged
configmap/grafana-dashboard-definition-knative unchanged
configmap/grafana-datasources unchanged
configmap/grafana-dashboards unchanged
deployment.apps/grafana configured
configmap/prometheus-scrape-config unchanged
service/kube-controller-manager unchanged
service/prometheus-system-discovery unchanged
serviceaccount/prometheus-system unchanged
role.rbac.authorization.k8s.io/prometheus-system unchanged
role.rbac.authorization.k8s.io/prometheus-system unchanged
role.rbac.authorization.k8s.io/prometheus-system unchanged
role.rbac.authorization.k8s.io/prometheus-system unchanged
clusterrole.rbac.authorization.k8s.io/prometheus-system unchanged
rolebinding.rbac.authorization.k8s.io/prometheus-system unchanged
rolebinding.rbac.authorization.k8s.io/prometheus-system unchanged
rolebinding.rbac.authorization.k8s.io/prometheus-system unchanged
rolebinding.rbac.authorization.k8s.io/prometheus-system unchanged
clusterrolebinding.rbac.authorization.k8s.io/prometheus-system unchanged
service/prometheus-system-np unchanged
statefulset.apps/prometheus-system configured
service/zipkin created
deployment.apps/zipkin configured
The Service "grafana" is invalid: spec.ports[0].nodePort: Forbidden: may not be used when `type` is 'ClusterIP'
```
