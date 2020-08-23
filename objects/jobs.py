import sys, time, os, getopt
start_time = time.time()
from modules import logging as logger
from modules import process as k8s
from modules.get_jobs import K8sJobs

class Jobs:
    def __init__(self,ns):
        global k8s_object_list, namespace
        self.ns = ns
        if not ns:
            ns = 'all' 
        namespace = ns   
        k8s_object_list = K8sJobs.get_jobs(ns)
        if not len(k8s_object_list.items):
            print ("[WARNING] No jobs found.")
            sys.exit()
    global k8s_object, _logger
    _logger = logger.get_logger('Jobs')
    k8s_object = 'jobs'

    def list_jobs(v, l):
        data = []
        headers = ['NAMESPACE', 'JOBS']
        for item in k8s_object_list.items:
            data.append([item.metadata.namespace, item.metadata.name])
        data = k8s.Output.append_hyphen(data, '---------')
        data.append(["Total: " , len(data) - 1])
        k8s.Output.print_table(data, headers, True, l)

    def check_jobs_pod_security(v, l):
        headers = ['NAMESPACE', 'JOBS', 'CONTAINER_NAME', 'PRIVILEGED_ESC', \
        'PRIVILEGED', 'READ_ONLY_FS', 'RUN_AS_NON_ROOT', 'RUNA_AS_USER']        
        data = k8s.Check.security_context(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)

    def check_jobs_pod_health_probes(v, l):
        headers = ['NAMESPACE', 'JOBS', 'CONTAINER_NAME', 'READINESS_PROPBE', \
        'LIVENESS_PROBE']        
        data = k8s.Check.health_probes(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data) 

    def check_jobs_pod_resources(v, l): 
        headers = ['NAMESPACE', 'JOBS', 'CONTAINER_NAME', 'LIMITS', 'REQUESTS']       
        data = k8s.Check.resources(k8s_object, k8s_object_list, headers, \
        v, namespace, l)
        if l: _logger.info(data)         

    def check_jobs_pod_tolerations_affinity_node_selector_priority(v, l): 
        headers = ['NAMESPACE', 'JOBS', 'NODE_SELECTOR', 'TOLERATIONS', \
        'AFFINITY', 'PRIORITY_CLASS']     
        data = k8s.Check.tolerations_affinity_node_selector_priority(k8s_object, \
        k8s_object_list, headers, v, namespace, l)
        if l: _logger.info(data)

def call_all(v, ns, l):
    Jobs(ns)
    Jobs.list_jobs(v, l)
    Jobs.check_jobs_pod_security(v, l)
    Jobs.check_jobs_pod_health_probes(v, l)
    Jobs.check_jobs_pod_resources(v, l)
    Jobs.check_jobs_pod_tolerations_affinity_node_selector_priority(v, l)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvn:l", ["help", "verbose", \
        "namespace", "logging"])
        if not opts:        
            call_all('','','')
            k8s.Output.time_taken(start_time)
            sys.exit()
            
    except getopt.GetoptError as err:
        print(err)
        return
    verbose, ns, l= '', '', ''
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-n", "--namespace"):
            ns = a
        elif o in ("-l", "--logging"):
            l = True                  
        else:
            assert False, "unhandled option"
    call_all(verbose, ns, l)
    k8s.Output.time_taken(start_time)      

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " \
        + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)