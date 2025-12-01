import os
import json
from aiohttp import web
from server import PromptServer

from ..log import log

# Define where to save presets.
# Saving in the root of the extension or a user directory.
# Let's save in a 'user' directory in the extension root.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
# Back up to root from server/
ROOT_DIR = os.path.abspath(f'{THIS_DIR}/../../')
USER_DIR = os.path.join(ROOT_DIR, 'user')
PRESETS_FILE = os.path.join(USER_DIR, 'lora_presets.json')

if not os.path.exists(USER_DIR):
    try:
        os.makedirs(USER_DIR)
    except Exception as e:
        log(f"Error creating user directory: {e}", color="RED")

routes = PromptServer.instance.routes

def get_presets():
    if not os.path.exists(PRESETS_FILE):
        return []
    try:
        with open(PRESETS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"Error reading presets file: {e}", color="RED")
        return []

def save_presets(presets):
    try:
        with open(PRESETS_FILE, 'w') as f:
            json.dump(presets, f, indent=2)
        return True
    except Exception as e:
        log(f"Error writing presets file: {e}", color="RED")
        return False

@routes.get('/rgthree/api/lora/presets')
async def api_get_presets(request):
    presets = get_presets()
    return web.json_response(presets)

@routes.post('/rgthree/api/lora/presets')
async def api_save_preset(request):
    data = None
    # Handle both application/json and multipart/form-data (rgthreeApi.postJson)
    if request.content_type == 'application/json':
        try:
             data = await request.json()
        except:
             pass
    else:
        try:
            post = await request.post()
            json_str = post.get("json")
            if json_str:
                data = json.loads(json_str)
        except Exception:
            pass

    if data is None:
         return web.json_response({"error": "Invalid data"}, status=400)

    # data should be { "name": "preset name", "loras": [...] }
    if 'name' not in data or 'loras' not in data:
         return web.json_response({"error": "Missing name or loras field"}, status=400)

    presets = get_presets()

    # Check if preset exists and update, or add new
    existing_idx = next((i for i, p in enumerate(presets) if p['name'] == data['name']), -1)

    if existing_idx >= 0:
        presets[existing_idx] = data
    else:
        presets.append(data)

    if save_presets(presets):
        return web.json_response({"status": "ok", "presets": presets})
    else:
        return web.json_response({"error": "Failed to save preset"}, status=500)

@routes.delete('/rgthree/api/lora/presets')
async def api_delete_preset(request):
    data = None
    try:
         if request.can_read_body:
             data = await request.json()
    except Exception:
         pass

    # Support both json body and query param
    name = None
    if data:
        name = data.get('name')

    if not name:
        name = request.query.get('name')

    if not name:
        return web.json_response({"error": "Missing name"}, status=400)

    presets = get_presets()
    initial_len = len(presets)
    presets = [p for p in presets if p['name'] != name]

    if len(presets) == initial_len:
         return web.json_response({"error": "Preset not found"}, status=404)

    if save_presets(presets):
         return web.json_response({"status": "ok", "presets": presets})
    else:
        return web.json_response({"error": "Failed to save preset"}, status=500)
