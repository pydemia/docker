
alias kubectl-me="kubectl config current-context;kubectl cluster-info"
alias kme="kubectl-me"
alias k="kubectl"

function kns () { 
  NAMESPACE="${1:-default}"
  kubectl config set-context --current --namespace="${NAMESPACE}"
}

# # "kubectl -n istio-system get gw ingress-prd -o jsonpath='{.metadata.annotations.kubectl\.kubernetes\.io/last-applied-configuration}' | yq -y"

function kx () {
  NAMESPACE="$1"
  # SELECTOR="model=skh-bch-003"
  SELECTOR="$2"
  CMD="${3:-/bin/bash}"
  kubectl -n ${NAMESPACE} exec --stdin --tty "$(kubectl -n ${NAMESPACE} get pods -l ${SELECTOR} -o jsonpath='{.items[0].metadata.name}')" -- ${CMD}
}

function kxc () {
  NAMESPACE="$1"
  # SELECTOR="model=skh-bch-003"
  SELECTOR="$2"
  CONTAINER="$3"
  CMD="${4:-/bin/bash}"
  kubectl -n ${NAMESPACE} exec --stdin --tty "$(kubectl -n ${NAMESPACE} get pods -l ${SELECTOR} -o jsonpath='{.items[0].metadata.name}')" -c ${CONTAINER} -- ${CMD}
}

function kxp () {
  NAMESPACE="$1"
  # SELECTOR="model=skh-bch-003"
  PODNAME="$2"
  CONTAINER="$3"
  CMD="${4:-/bin/bash}"
  kubectl -n ${NAMESPACE} exec --stdin --tty ${PODNAME} -c ${CONTAINER} -- ${CMD}
}

function kdb () {
  NAMESPACE="${1:-default}"
  kubectl -n ${NAMESPACE} run --rm -it debug --image=pydemia/debug --restart=Never
}

function kds () {
  NAMESPACE="${1:-default}"
  kubectl -n ${NAMESPACE} run --rm -it debug --image=pydemia/debug-slim --restart=Never
}

