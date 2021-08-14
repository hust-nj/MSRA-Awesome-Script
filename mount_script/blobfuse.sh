# for unmount: fusermount -u /dev/cloudstorage
AZURE_STORAGE_ACCOUNT_arr=(your_account)
AZURE_STORAGE_ACCESS_KEY_arr=(
account_key
)

export AZURE_STORAGE_ACCOUNT=${AZURE_STORAGE_ACCOUNT_arr[0]}
export AZURE_STORAGE_ACCESS_KEY=${AZURE_STORAGE_ACCESS_KEY_arr[0]}
for folder in v-jining; do
    mount_folder=${HOME}/blobfuse/${AZURE_STORAGE_ACCOUNT}/${folder}
    mkdir -p ${mount_folder}
    blobfuse ${mount_folder} \
        --container-name=${folder} \
        --tmp-path=${HOME}/blobfuse/resource/blobfusetmp_v-jining/${AZURE_STORAGE_ACCOUNT}/${folder} \
        -o attr_timeout=240 \
        -o entry_timeout=240 \
        -o negative_timeout=120
done
