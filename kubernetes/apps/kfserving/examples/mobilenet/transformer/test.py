# %%
import json
import transform_fn as trn

# %%

with open('../input.json', 'r') as f:
  request_string = json.load(f)
  # res = {
  #   'instances': [
  #     {'input_1': string}
  #   ]
  # }

with open('../output_without_postprocessing.json', 'r') as f:
  response_string = json.load(f)
  # res = {
  #   'instances': [
  #     {'input_1': string}
  #   ]
  # }

# %%
trn.preprocess_fn(request_string)

request_transformed = {
  'instances': [
    trn.preprocess_fn(i) for i in request_string['instances']
  ]
}

trn.postprocess_fn(response_string)


request_transformed = {
    'predictions': [
        trn.postprocess_fn(p) for p in response_string['predictions']
    ]
}
