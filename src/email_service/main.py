import os
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from jinja2 import Environment, FileSystemLoader, select_autoescape
from dotenv import load_dotenv

# Env vars
load_dotenv()   # For local development, ensure .env is loaded.
API_KEY = os.getenv("API_KEY")
EMAIL_API_URL = os.getenv("EMAIL_API_URL", "https://api.brevo.com/v3/smtp/email")

if not API_KEY:
    raise RuntimeError("API_KEY must be set in environment")

# Setup FastAPI
app = FastAPI(title="Email Service")

# Jinja2 template env
env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(["html", "xml"])
)

# Request payload
class EmailRequest(BaseModel):
    to: str
    subject: str
    template: str  # e.g. "confirmation"
    variables: dict


def render_template(template_name: str, variables: dict) -> dict:
    """Render both text and HTML parts from templates folder."""
    result = {}

    txt_template = f"{template_name}.txt.j2"
    html_template = f"{template_name}.html.j2"

    if os.path.exists(os.path.join("templates", txt_template)):
        result["textContent"] = env.get_template(txt_template).render(**variables)

    if os.path.exists(os.path.join("templates", html_template)):
        result["htmlContent"] = env.get_template(html_template).render(**variables)

    if not result:
        raise FileNotFoundError(f"No templates found for {template_name}")

    return result


@app.post("/send")
async def send_email(req: EmailRequest):
    try:
        body = render_template(req.template, req.variables)

        payload = {
            "sender": {"name": "Jay0.dev Notifications", "email": "noreply@jay0.dev"},
            "to": [{"email": req.to}],
            "subject": req.subject,
            **body
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                EMAIL_API_URL,
                headers={
                    "accept": "application/json",
                    "content-type": "application/json",
                    "api-key": API_KEY,
                },
                json=payload,
            )
            resp.raise_for_status()

        return {"status": "sent", "to": req.to, "template": req.template}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
