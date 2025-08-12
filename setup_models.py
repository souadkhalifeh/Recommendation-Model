import os
import gdown

os.makedirs("fine_tuned_price_model", exist_ok=True)

gdown.download_folder(
    url="https://drive.google.com/drive/folders/1pj8NhiRpjP2q304zyEwZWAbtdG3Mp0Na",
    output="fine_tuned_price_model",
    quiet=False,
    use_cookies=False
)

gdown.download(
    url="https://drive.google.com/uc?id=1_VrIIAkPyyNIZKCQ_fSVchwBo7cEiVul",
    output="sbert_text_embeddings.npy",
    quiet=False
)

gdown.download(
    url="https://drive.google.com/uc?id=1hHBFYhfnpSjvyBDM5prGuzPxWp123ZuJ",
    output="swap_dataset.csv",
    quiet=False
)
