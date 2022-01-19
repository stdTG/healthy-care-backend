from fastapi import HTTPException, Header


def workspace_header(Workspace: str = Header("ignilife")):
    if not Workspace:
        raise HTTPException(status_code=400, detail="Workspace header invalid")
