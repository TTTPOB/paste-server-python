import httpx
from Crypto.PublicKey import RSA
from Crypto.Cipher import ChaCha20, PKCS1_OAEP
from pathlib import Path
from hashlib import sha256
import websockets as ws
import os
import asyncio

SERVER = "127.0.0.1:8000"
CONFIGDIR = (
    Path(os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")))
    / "paste-client"
)
KEYDIR = CONFIGDIR / "keys"


class paste_client:
    def __init__(self, userid):
        self.userid = userid
        self.keypair = self.get_or_generate_keypair()
        sha256_ = sha256()
        sha256_.update(self.keypair["pubkey"].encode("utf-8"))
        self.pubkey_hash = sha256_.hexdigest()
        self.url = f"http://{SERVER}"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Paste Client",
        }

    def get_or_generate_keypair(self):
        """
        fetch the key pair from KEYDIR, if they are not present, generate a 4096bit
        RSA key pair
        """
        if not KEYDIR.exists():
            KEYDIR.mkdir(parents=True, exist_ok=True)

        pubkey_path = KEYDIR / f"{self.userid}.pub"
        privkey_path = KEYDIR / f"{self.userid}.priv"
        if pubkey_path.exists() and privkey_path.exists():
            print("Found keypair, read it")
            pubkey = pubkey_path.read_text()
            privkey = privkey_path.read_text()
            return {"pubkey": pubkey, "privkey": privkey}
        else:
            print("No keypair found, generating 4096bit RSA keypair")
            print("Hit enter to continue")
            input()
            keypair = RSA.generate(4096)
            pubkey = keypair.publickey().export_key().decode("utf-8")
            privkey = keypair.export_key().decode("utf-8")
            pubkey_path.write_text(pubkey)
            privkey_path.write_text(privkey)
            return {"pubkey": pubkey, "privkey": privkey}

    def register(self):
        device_data = {"userid": self.userid, "pubkey": self.keypair["pubkey"]}
        resp = httpx.post(
            f"{self.url}/register", json=device_data, headers=self.headers
        )
        if httpx.codes.ok:
            print("Successfully registered")
            print(f"Registration information: {resp.text}")
    def connect(self):
        self.wsurl=f"{self.url}/ws/{self.userid}/{self.pubkey_hash}".replace("http", "ws")
        self.ws = ws.connect(self.wsurl)
        print(self.wsurl)
    async def send(self, message):
        async with self.ws as ws:
            await ws.send(message)


async def main():   
    client = paste_client("tpob")
    client.register()
    client.connect()
    await client.send("hello")
    
    

if __name__ == "__main__":
    asyncio.run(main())