import { NextRequest } from "next/server";

const AG_UI_SERVICE_URL = process.env.AG_UI_SERVICE_URL ?? "http://127.0.0.1:8000/ag-ui/chat";

export async function POST(request: NextRequest) {
  const body = await request.text();
  const accept = request.headers.get("accept") ?? "text/event-stream";

  const response = await fetch(AG_UI_SERVICE_URL, {
    method: "POST",
    headers: {
      "content-type": request.headers.get("content-type") ?? "application/json",
      "accept": accept
    },
    body
  });

  return new Response(response.body, {
    status: response.status,
    headers: {
      "content-type": response.headers.get("content-type") ?? accept,
      "cache-control": "no-cache"
    }
  });
}
