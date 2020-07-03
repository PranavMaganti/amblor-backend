import asyncio

from fastapi import FastAPI, Response
import uvicorn

from modules.lastfm import import_tracks

app = FastAPI()


@app.get("/import/lastfm/")
async def import_lastfm(username: str):
    loop = asyncio.get_event_loop()
    loop.create_task(import_tracks(username))
    return Response(content="This will take 2-3 minutes", media_type="application/text")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
