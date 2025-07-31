import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { stream } = body;

    // Determine if we should use streaming endpoint
    const endpoint = stream ? "chat/stream" : "chat";
    
    // For streaming responses, we need to forward the stream directly
    if (stream) {
      const backendRes = await fetch(`https://airtel-chatbot-backend-a6dr.onrender.com/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: body.session_id,
          message: body.message
        }),
      });
      
      // Create a TransformStream to forward the SSE events
      const { readable, writable } = new TransformStream();
      
      // Pipe the response to our transform stream
      backendRes.body?.pipeTo(writable);
      
      // Return a streaming response
      return new Response(readable, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        },
      });
    } else {
      // Non-streaming response (original behavior)
      const backendRes = await fetch(`http://localhost:8000/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: body.session_id,
          message: body.message
        }),
      });
      const data = await backendRes.json();
      return NextResponse.json(data, { status: 200 });
    }
  } catch (error) {
    const err = error as Error;
    console.error(`API route error: ${err.message}`);
    return NextResponse.json(
      { error: err.message || "Internal server error" },
      { status: 500 }
    );
  }
}