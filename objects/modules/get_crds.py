from kubernetes import client, config
from kubernetes.client.rest import ApiException

config.load_kube_config()
crd = client.ApiextensionsV1beta1Api()

class K8sCRDs:
    def get_crds():
        try:
            print ("\n[INFO] Fetching all crds data...")
            crds = crd.list_custom_resource_definition(timeout_seconds=10)
            return crds
        except ApiException as e:
            print("Exception when calling ApiextensionsV1Api->list_custom_resource_definition: %s\n" % e)
      