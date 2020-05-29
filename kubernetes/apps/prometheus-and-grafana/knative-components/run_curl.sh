#!/bin/bash

SVC_NAME="sklearn-iris" && \
SVC_NS="pavin" && \
cat <<EOF
{
	"account" : "",
	"name" : "$SVC_NAME",
	"namespace" : "$SVC_NS",
	"concurrent" : "10",
	"defaultSpec" : [{
		"predictor" : [{
			"loggerMode" : "all",
			"loggerUrl" : "http://message-dumper.default",
			"minReplica" : "1",
			"maxReplica" : "1",
			"predictorType" : "sklearn",
			"runtimeVersion" : "v0.3.0",
			"storageUri" : "gs://kfserving-samples/models/sklearn/iris",
			"resources" : [{
				"limits" : [{"cpu" : "100m", "memory" : "1Gi", "gpu" : "0"}],
				"requests" : [{"cpu" : "100m", "memory" : "1Gi", "gpu" : "0"}]
			}]
		}]
	}],
	"canarySpec": [{"":""}],
	"canaryTrafficPercent" : "0"
}
EOF

SVC_NAME="sklearn-iris" && \
SVC_NS="pavin" && \
curl -i \
    -X POST http://localhost:8080/deploy \
    -H "Content-Type:application/json" \
    -d @- <<EOF
{
	"account" : "",
	"name" : "$SVC_NAME",
	"namespace" : "$SVC_NS",
	"concurrent" : "10",
	"defaultSpec" : [{
		"predictor" : [{
			"loggerMode" : "all",
			"loggerUrl" : "http://message-dumper.default",
			"minReplica" : "1",
			"maxReplica" : "1",
			"predictorType" : "sklearn",
			"runtimeVersion" : "v0.3.0",
			"storageUri" : "gs://kfserving-samples/models/sklearn/iris",
			"resources" : [{
				"limits" : [{"cpu" : "100m", "memory" : "1Gi", "gpu" : "0"}],
				"requests" : [{"cpu" : "100m", "memory" : "1Gi", "gpu" : "0"}]
			}]
		}]
	}],
	"canarySpec": [{"":""}],
	"canaryTrafficPercent" : "0"
}
EOF