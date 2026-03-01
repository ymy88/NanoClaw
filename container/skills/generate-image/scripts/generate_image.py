#!/usr/bin/env python3
"""Generate an image using Gemini via Vertex AI."""

import argparse
import sys

from google import genai
from google.genai import types


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Image generation prompt")
    parser.add_argument("-o", "--output", default="/workspace/group/generated_image.png",
                        help="Output file path (must be under /workspace/group/)")
    args = parser.parse_args()

    import os
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/tmp/gcloud-credentials.json")
    if not os.path.exists(creds_path):
        print("Error: Vertex AI is not configured. No credentials file found at "
              f"{creds_path}. Ask the admin to set up Vertex AI (add "
              "GOOGLE_APPLICATION_CREDENTIALS to .env).", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(vertexai=True, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=args.prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )

    # Check for errors
    if response.candidates[0].finish_reason != types.FinishReason.STOP:
        reason = response.candidates[0].finish_reason
        print(f"Error: {reason}", file=sys.stderr)
        sys.exit(1)

    for part in response.candidates[0].content.parts:
        if part.thought:
            continue
        if part.inline_data:
            with open(args.output, "wb") as f:
                f.write(part.inline_data.data)
            print(args.output)
            return

    print("Error: no image was generated", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
