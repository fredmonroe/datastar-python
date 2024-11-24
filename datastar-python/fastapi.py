from fastapi import Request, HTTPException
import json
from typing import Any

__all__ = ["ReadSignals"]


async def ReadSignals(request: Request) -> dict[str, Any]:
    """
    Parses incoming data from the browser and returns it as a dictionary.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        Dict[str, Any]: Parsed data from the request.

    Raises:
        HTTPException: If the data is invalid or improperly formatted.


    example of use:
    @app.post("/parse-signals")
    async def parse_signals(parsed_signals: Dict[str, Any] = Depends(ReadSignals)):

    """
    try:
        if request.method == "GET":
            # Parse query string for the "datastar" key
            datastar_value = request.query_params.get("datastar")
            if not datastar_value:
                raise HTTPException(
                    status_code=400, detail="Missing 'datastar' key in query parameters"
                )
            # Decode the URL-encoded JSON string
            parsed_data: dict[str, Any] = json.loads(datastar_value)
        else:
            # Parse the body as JSON
            parsed_data = await request.json()

        return parsed_data

    except json.JSONDecodeError:
        # Handle invalid JSON
        raise HTTPException(status_code=400, detail="Invalid JSON data in request")
