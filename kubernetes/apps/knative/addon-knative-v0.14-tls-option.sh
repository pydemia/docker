# # 4. Configure DNS: Magic DNS (`xip.io`)
# curl -sL https://github.com/knative/serving/releases/download/${VERSION}/serving-default-domain.yaml -O && \
#     kubectl apply -f serving-default-domain.yaml
# 4. Real DNS
# 4-A. If the networking layer produced an External IP address,
# then configure a wildcard A record for the domain:
# (Here knative.example.com is the domain suffix for your cluster)
# *.knative.example.com == A 35.233.41.212
# 4-B. If the networking layer produced a CNAME,
# then configure a CNAME record for the domain:
# *.knative.example.com == CNAME a317a278525d111e89f272a164fd35fb-1510370581.eu-central-1.elb.amazonaws.com

# # Replace knative.example.com with your domain suffix
# kubectl patch configmap/config-domain \
#   --namespace knative-serving \
#   --type merge \
#   --patch '{"data":{"knative.example.com":""}}'

# # TLS cert-manager
curl -sL https://github.com/knative/serving/releases/download/${VERSION}/serving-cert-manager.yaml -O && \
    kubectl apply -f serving-cert-manager.yaml
# TLS via HTTP01
curl https://github.com/knative/net-http01/releases/download/${VERSION}/release.yaml 0 serving-http01.yaml && \
    kubectl apply --filename serving-http01.yaml
# TLS wildcard
curl -sL https://github.com/knative/serving/releases/download/${VERSION}/serving-nscert.yaml -O && \
    kubectl apply -f serving-nscert.yaml
