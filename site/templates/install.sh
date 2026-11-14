# Recipient: run each step separately. Stop if a command fails.
curl --fail --location --remote-name 'https://github.com/MoonKibong/mumu-releases/releases/download/v0.1.0/mumu-0.1.0-py3-none-any.whl'
curl --fail --location --remote-name 'https://github.com/MoonKibong/mumu-releases/releases/download/v0.1.0/SHA256SUMS'
curl --fail --location --remote-name 'https://github.com/MoonKibong/mumu-releases/releases/download/v0.1.0/LICENSE'
curl --fail --location --remote-name 'https://github.com/MoonKibong/mumu-releases/releases/download/v0.1.0/NOTICE'
curl --fail --location --remote-name 'https://github.com/MoonKibong/mumu-releases/releases/download/v0.1.0/DISTRIBUTION-NOTICE.txt'
curl --fail --location --remote-name 'https://github.com/MoonKibong/mumu-releases/releases/download/v0.1.0/RELEASE-NOTES.txt'
python3.11 -c 'import hashlib,pathlib; rows=[line.split("  ") for line in pathlib.Path("SHA256SUMS").read_text().splitlines()]; expected={"mumu-0.1.0-py3-none-any.whl","DISTRIBUTION-NOTICE.txt","RELEASE-NOTES.txt","LICENSE","NOTICE","mumu-0.1.0-client-source.zip"}; assert len(rows)==len(expected) and {n for h,n in rows}==expected; assert all(hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest()==h for h,n in rows if n!="mumu-0.1.0-client-source.zip"); print("SHA-256 OK")'
python3.11 -m venv "$HOME/.local/share/mumu/0.1.0"
"$HOME/.local/share/mumu/0.1.0/bin/python" -m pip install './mumu-0.1.0-py3-none-any.whl'
. "$HOME/.local/share/mumu/0.1.0/bin/activate"
command -v mumu
mumu --help
python -c 'import importlib.metadata; assert importlib.metadata.version("mumu")=="0.1.0"; print("0.1.0")'
