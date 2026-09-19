from huggingface_hub import snapshot_download

path = snapshot_download(
    repo_id="RichardSakaguchiMS/brazilian-customer-service-conversations",
    # confirme o nome exato do arquivo no repo do HF
    repo_type="dataset",
    local_dir="./data"
)


print(path)