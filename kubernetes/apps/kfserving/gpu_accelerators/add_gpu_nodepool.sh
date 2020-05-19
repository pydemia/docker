
CLUSTER="kfserving-dev"
REGION="us-central1"
#ZONE="us-central1-a"
NODE_LOCATIONS="us-central1-a,us-central1-b,us-central1-f"
NODE_TAINTS="nvidia.com/gpu=present:NoSchedule,preemptible=true:NoSchedule"


ACCELERATOR_TYPE="nvidia-tesla-t4"
ACCELERATOR_COUNT="1"
NUM_NODES="2"
MIN_NODES="0"
MAX_NODES="5"

DISK_TYPE="pd-standard"  #  pd-standard, pd-ssd
DISK_SIZE="40GB"  # default: 100GB
IMAGE_TYPE="UBUNTU"  # COS, UBUNTU, COS_CONTAINERD, UBUNTU_CONTAINERD, WINDOWS_SAC, WINDOWS_LTSC (gcloud container get-server-config)
MACHINE_TYPE="n1-standard-4" # 4CPUs, 16GB (gcloud compute machine-types list) <https://cloud.google.com/compute/vm-instance-pricing>
SERVICE_ACCOUNT="yjkim-kube-admin-sa@ds-ai-platform.iam.gserviceaccount.com"
MAX_PODS_PER_NODE="110"

WORKLOAD_POOL="${PROJECT_ID}.svc.id.goog"
WORKLOAD_METADATA="GKE_METADATA"
METADATA="disable-legacy-endpoints=true"
LABELS="cz_owner=youngju_kim,application=kfserving,gpu=t4"
TAGS="yjkim-kube-instance,yjkim-kube-istio,yjkim-kube-knative,yjkim-kube-kafka,yjkim-kube-subnetall"

gcloud container node-pools create preemptible-gpu-t4-nodepool \
    --preemptible \
    --cluster $CLUSTER \
    --node-taints=$NODE_TAINTS \
    --accelerator type=$ACCELERATOR_TYPE,count=$ACCELERATOR_COUNT \
    --region $REGION \
    --node-locations $NODE_LOCATIONS \
    --num-nodes $NUM_NODES --min-nodes $MIN_NODES --max-nodes $MAX_NODES \
    --enable-autoscaling \
    --service-account=$SERVICE_ACCOUNT \
    --enable-autorepair \
    --no-enable-autoupgrade \
    --machine-type $MACHINE_TYPE \
    --disk-type $DISK_TYPE \
    --disk-size $DISK_SIZE \
    --image-type $IMAGE_TYPE \
    --workload-metadata $WORKLOAD_METADATA \
    --metadata=$METADATA \
    --max-pods-per-node $MAX_PODS_PER_NODE \
    --node-labels=$LABELS \
    --tags=$TAGS