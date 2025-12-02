VERSION = "0.0.1"
NAME = "rgthree-comfy"

async def get_logo_svg():
    return """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect x="0" y="0" width="100" height="100" fill="{bg}"/>
<text x="50" y="50" fill="{fg}" font-size="20" text-anchor="middle" alignment-baseline="middle">rgthree</text>
</svg>"""
