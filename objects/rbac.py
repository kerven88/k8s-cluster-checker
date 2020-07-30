from kubernetes.client.rest import ApiException
import sys, time, os, getopt, argparse, re
start_time = time.time()
from modules import process as k8s
from modules.get_rbac import K8sClusterRole, K8sClusterRoleBinding, \
K8sNameSpaceRole, K8sNameSpaceRoleBinding

class ClusterRole:
    global role_list
    role_list = K8sClusterRole.list_cluster_role()
    k8s_object = "clusteroles"
    def get_cluster_role(v):
        data = []
        headers = ['CLUSTER_ROLE', 'RULES', 'API_GROUPS', 'RESOURCES', 'VERBS']

        for item in role_list.items:
            if item.rules:
                rules = k8s.Rbac.get_rules(item.rules)            
                data.append([item.metadata.name, len(item.rules), \
                rules[0], rules[1], rules[2]])
            else:
                data.append([item.metadata.name, "-", "-", "-", "-"])
        k8s.Rbac.analyse_role(data,ClusterRole.k8s_object) 
        data.append(['----------', '---', '---', '---', '---'])
        data.append(["Total: " + str(len(role_list.items)), rules[3], "-", "-", "-"])
  
        k8s.Output.print_table(data,headers,v)

class ClusterRoleBinding:
    global role_binding_list
    role_binding_list = K8sClusterRoleBinding.list_cluster_role_binding()

    def get_cluster_role_binding(v): 
        data, rules_count = [], 0
        headers = ['CLUSTER_ROLE_BINDING', 'CLUSTER_ROLE', \
        'SERVICE_ACCOUNT', 'NAMESPACE']
        
        for item in role_binding_list.items:
            if item.subjects:
                for i in item.subjects:
                    data.append([item.metadata.name, item.role_ref.name, \
                    i.name, i.namespace])
            else:
                data.append([item.metadata.name, item.role_ref.name, '', ''])
        data.append(['----------', '---', '---', '---'])
        data.append(["Total: " + str(len(role_binding_list.items)), "-", "-", "-"])                 
        k8s.Output.print_table(data,headers,v)
        

class NsRole:
    def __init__(self,ns):
        global ns_role_list
        self.ns = ns
        if not ns:
            ns = 'all' 
        ns_role_list = K8sNameSpaceRole.list_namespaced_role(ns)
 
    global k8s_object
    k8s_object = 'roles'

    def get_ns_role(v):    
        data = []
        headers = ['ROLE', 'NAMESPACE', 'RULES', 'API_GROUPS', 'RESOURCES', 'VERBS']
        for item in ns_role_list.items:
            if item.rules:
                rules = k8s.Rbac.get_rules(item.rules)
                data.append([item.metadata.name, item.metadata.namespace, \
                len(item.rules), rules[0], rules[1], rules[2]])
            else:
                data.append([item.metadata.name, item.metadata.namespace, "-", "-", "-", "-"])
        k8s.Rbac.analyse_role(data,k8s_object)
        data.append(['----------', '---', '---', '---', '---', '---'])
        data.append(["Total: " + str(len(ns_role_list.items)), "-", "-", "-",  "-", "-"])          
        k8s.Output.print_table(data,headers,v)

class NsRoleBinding:
    def __init__(self,ns):
        global ns_role_binding_list
        self.ns = ns
        if not ns:
            ns = 'all'
        ns_role_binding_list = K8sNameSpaceRoleBinding.list_namespaced_role_binding(ns)
    
    def get_ns_role_binding(v):      
        data = []
        headers = ['ROLE_BINDING', 'NAMESPACE', 'ROLE', 'GROUP_BINDING']
        for item in ns_role_binding_list.items:
            if item.subjects:
                subjects = ""
                for i in item.subjects:
                    if len(item.subjects) > 1:
                        subjects = subjects + i.name + '\n'
                    else:
                        subjects = i.name
                data.append([item.metadata.name, item.metadata.namespace, \
                item.role_ref.name, subjects])
            else:
                data.append([item.metadata.name, item.metadata.namespace, \
                item.role_ref.name, 'None'])
        data.append(['----------', '---', '---', '---'])
        data.append(["Total: " + str(len(ns_role_binding_list.items)), "-", "-", "-"]) 
        k8s.Output.print_table(data,headers,v)

def call_all(v,ns):     
    if not ns:
        ClusterRole.get_cluster_role(v)
        ClusterRoleBinding.get_cluster_role_binding(v)

    NsRole(ns)
    NsRole.get_ns_role(v)
    NsRoleBinding(ns)
    NsRoleBinding.get_ns_role_binding(v)
    headers = ['CLUSTER_ROLE', 'CLUSTER_ROLE_BINDING', 'ROLE', 'ROLE_BINDING']
    k8s.Output.print_table([[len(role_list.items), len(role_binding_list.items), \
    len(ns_role_list.items), len(ns_role_binding_list.items)]],headers,True)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvn:", ["help", "verbose", "namespace"])
        if not opts:        
            call_all("","")
            sys.exit()
            
    except getopt.GetoptError as err:
        print(err)
        return
    verbose, ns = '', ''
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-n", "--namespace"):
            if not verbose: verbose = False
            ns = a          
        else:
            assert False, "unhandled option"
    call_all(verbose,ns)
    k8s.Output.time_taken(start_time)     

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(k8s.Output.RED + "[ERROR] " + k8s.Output.RESET + 'Interrupted from keyboard!')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)