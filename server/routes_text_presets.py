import os
import json
from aiohttp import web
from server import PromptServer
from ..log import log

# Define where to save text presets.
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(f'{THIS_DIR}/../../')
USER_DIR = os.path.join(ROOT_DIR, 'user')
TEXT_PRESETS_FILE = os.path.join(USER_DIR, 'power_text_presets.json')

if not os.path.exists(USER_DIR):
    try:
        os.makedirs(USER_DIR)
    except Exception as e:
        log(f"Error creating user directory: {e}", color="RED")

routes = PromptServer.instance.routes

def get_text_presets():
    if not os.path.exists(TEXT_PRESETS_FILE):
        return {}
    try:
        with open(TEXT_PRESETS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        log(f"Error reading text presets file: {e}", color="RED")
        return {}

def save_text_presets(presets):
    try:
        with open(TEXT_PRESETS_FILE, 'w') as f:
            json.dump(presets, f, indent=2)
        return True
    except Exception as e:
        log(f"Error writing text presets file: {e}", color="RED")
        return False

@routes.get('/power/api/text/presets')
async def api_get_text_presets(request):
    presets = get_text_presets()
    return web.json_response(presets)

@routes.post('/power/api/text/presets')
async def api_save_text_preset(request):
    data = None
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

    # Expect: { "category": "...", "name": "...", "text": "..." }
    category = data.get('category')
    name = data.get('name')
    text = data.get('text')

    if not category or not name:
         return web.json_response({"error": "Missing category or name"}, status=400)

    presets = get_text_presets()

    if category not in presets:
        presets[category] = {}

    presets[category][name] = text

    if save_text_presets(presets):
        return web.json_response({"status": "ok", "presets": presets})
    else:
        return web.json_response({"error": "Failed to save preset"}, status=500)

@routes.delete('/power/api/text/presets')
async def api_delete_text_preset(request):
    data = None
    try:
         if request.can_read_body:
             data = await request.json()
    except Exception:
         pass

    # Support query params too?

    category = data.get('category') if data else None
    name = data.get('name') if data else None

    if not category:
         return web.json_response({"error": "Missing category"}, status=400)

    presets = get_text_presets()

    if category in presets:
        if name:
            if name in presets[category]:
                del presets[category][name]
            else:
                return web.json_response({"error": "Preset not found"}, status=404)
        else:
             # Delete entire category?
             del presets[category]
    else:
        return web.json_response({"error": "Category not found"}, status=404)

    if save_text_presets(presets):
         return web.json_response({"status": "ok", "presets": presets})
    else:
        return web.json_response({"error": "Failed to save preset"}, status=500)
