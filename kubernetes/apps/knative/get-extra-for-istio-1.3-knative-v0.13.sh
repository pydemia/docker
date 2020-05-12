#!/bin/bash

git clone --single-branch -b release-0.13 https://github.com/knative/serving third_party && \
  cd third_party && \
  git filter-branch --subdirectory-filter third_party HEAD && \
  cd .. && \
  mkdir -p knative-serving-extra-istio-1.3-latest && \
  cp -fL third_party/istio-1.3-latest/*.yaml ./knative-serving-extra-istio-1.3-latest && \
  rm -rf ./third_party

