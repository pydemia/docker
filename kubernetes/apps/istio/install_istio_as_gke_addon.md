
# Install `Istio` as GKE Add-on
In GKE, we can install `Istio` as Add-on.
```sh
$ gcloud beta container clusters create \
    ...
    --addons HttpLoadBalancing,Istio,... \
    --istio-config=$ISTIO_CONFIG \
    ...
```

:warning: But, there is `Third-party` extras in `Knative`. [Read the post.](https://medium.com/google-cloud/how-to-properly-install-knative-on-gke-f39a1274cd4f)
If you need `Knative==0.13` and `Istio>=1.3`, **You should install those FIRST, with a proper version.**
**Then, the required `Istio` version for `Knative` is differ from `GKE`.**

<https://github.com/knative/serving/tree/master/third_party>



| ![](../istio/gke-istio-vanilla.png) |
| ----- |


| ![](../knative/knative-third-party-0.13.png) |
| ----- |
| ![](../istio/gke-istio-version.png) |
