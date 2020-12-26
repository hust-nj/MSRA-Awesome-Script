au_dict = dict(
    resource_group  = "australiav100",
    workspace_name  = "australiav100ws"
)
kr_dict = dict(
    resource_group  = "koreav100",
    workspace_name  = "koreav100ws"
)
jp_dict = dict(
    resource_group  = "japanv100",
    workspace_name  = "japanv100ws"
)
ca_dict = dict(
    resource_group  = "canadav100",
    workspace_name  = "canadav100ws"
)
uss_dict = dict(
    resource_group  = "usscv100",
    workspace_name  = "usscv100ws"
)
ussc_dict= dict(
    resource_group  = "ussclowpriv100",
    workspace_name  = "ussclowpriv100ws"
)
itp_dict = dict(
    resource_group  = "researchvc",
    workspace_name  = "resrchvc"
)

cluster_dict = dict(
    australia24scl=au_dict,
    australiav100cl=au_dict,
    korea24cl=kr_dict,
    koreav100cl=kr_dict,
    japan24scl=jp_dict,
    japanv100cl=jp_dict,
    canada24=ca_dict,
    canadav100cl=ca_dict,
    usscv100cl=uss_dict,
    ussc40rscl=ussc_dict,
    itpseasiav100cl=itp_dict,
    itpeastusv100cl=itp_dict,
    itplabrr1cl1=itp_dict
)

# cluster_name = "itplabrr1cl1"
cluster_name = "itpeastusv100cl"
# cluster_name = "itpseasiav100cl"
base_gpus = 4 if cluster_name not in ("usscv100cl", "ussc40rscl", "itpseasiav100cl", "itpeastusv100cl", "itplabrr1cl1") else 8
num_gpus = 8

if cluster_name=="itplabrr1cl1": # rr1
    data_blob=dict(
        blob_container_name = "v-jining",
        blob_account_name   = "njrr1",
        blob_account_key    = "input your key",
    )
    datastore_name="nj_wu"
elif cluster_name=="itpseasiav100cl": # seasia
    data_blob=dict(
        blob_container_name = "v-jining",
        blob_account_name   = "binliu",
        blob_account_key    = "input your key",
    )
    datastore_name="nj_sea"
else: # eastus
    data_blob=dict( # eastus
        blob_container_name = "v-jining",
        blob_account_name = "jianing",
        blob_account_key = "input your key"
    )
    datastore_name="nj_eu"

config = dict(
    cluster_name=cluster_name,
    resource_group=cluster_dict[cluster_name]["resource_group"],
    workspace_name=cluster_dict[cluster_name]["workspace_name"],
    subscription_id="input your key" if cluster_name in ["itpseasiav100cl", "itpeastusv100cl", "itplabrr1cl1"] else "input your key" if cluster_name != "usscv100cl" else  "input your key",
    data_blob=data_blob,
    datastore_name=datastore_name,     # keep same in yaml and entry_script.
    experiment_name="condconv-reppoints",     # You can use any name here.
    custom_docker_image="ninja0/mmdet",    # docker address
    node_count=num_gpus // base_gpus,     # number of nodes
    process_count_per_node=base_gpus,     # number of gpu per node_count
    entry_path="./scripts",
    entry_file="base_script.py",
    params=dict(
        auth="input your key",
        branch="master",
        launcher="mpi" if ("24" in cluster_name or cluster_name in ("usscv100cl", "ussc40rscl", "itpseasiav100cl", "itpeastusv100cl")) else "infimpi",
        aml_work_dir_prefix="work_dirs/condconv-reppoints",
        aml_data_store=f"/{datastore_name}",
        script_path="./tools/train.py",
        config_files=[
            "configs/reppoints_v1_condconv/reppoints_condconv_minmax_r50_fpn_1x_coco.py"
        ],
        num_gpu=8
    )
)
