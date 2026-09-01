"""Messages de confirmation/erreur après redirection (pattern Post/Redirect/Get).

Portés dans la query string plutôt que dans une session : pas besoin de
gérer de cookies de session pour un MVP mono-poste partagé par l'équipe.
"""
from urllib.parse import urlencode

from starlette.responses import RedirectResponse


def redirect(
    url: str,
    message: str | None = None,
    error: bool = False,
    status_code: int = 303,
    **extra_params,
) -> RedirectResponse:
    params = {}
    if message:
        params["msg"] = message
        params["type"] = "error" if error else "success"
    params.update({k: v for k, v in extra_params.items() if v is not None})
    if params:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{urlencode(params)}"
    return RedirectResponse(url, status_code=status_code)
