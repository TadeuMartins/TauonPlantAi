
import httpx
from settings import settings

class SharePointClient:
    def __init__(self):
        self.tenant = settings.tenant_id
        self.client_id = settings.client_id
        self.client_secret = settings.client_secret
        self.site_host = settings.sp_site_host
        self.site_path = settings.sp_site_path
        self.drive_name = settings.sp_drive_name
        self.token = None

    async def _get_token(self):
        url = f"https://login.microsoftonline.com/{self.tenant}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        }
        async with httpx.AsyncClient() as c:
            r = await c.post(url, data=data)
            r.raise_for_status()
            self.token = r.json()["access_token"]

    async def _auth(self):
        if not self.token:
            await self._get_token()
        return {"Authorization": f"Bearer {self.token}"}

    async def iter_files(self, folder_path: str):
        async with httpx.AsyncClient(base_url="https://graph.microsoft.com/v1.0") as c:
            headers = await self._auth()
            site = await c.get(f"/sites/{self.site_host}:{self.site_path}", headers=headers)
            site.raise_for_status()
            site_id = site.json()["id"]
            drives = await c.get(f"/sites/{site_id}/drives", headers=headers)
            drives.raise_for_status()
            drive = next((d for d in drives.json()["value"] if d["name"] == self.drive_name), None)
            if not drive:
                raise RuntimeError("Drive not found")
            drive_id = drive["id"]
            root = await c.get(f"/drives/{drive_id}/root:/{folder_path}", headers=headers)
            root.raise_for_status()
            item_id = root.json()["id"]

            async def walk(item_id):
                children = await c.get(f"/drives/{drive_id}/items/{item_id}/children", headers=headers)
                children.raise_for_status()
                for it in children.json()["value"]:
                    if "folder" in it:
                        yield from (await walk(it["id"]))
                    else:
                        dl = await c.get(f"/drives/{drive_id}/items/{it['id']}/content", headers=headers)
                        dl.raise_for_status()
                        yield it["name"], dl.content

            async for f in walk(item_id):
                yield f
