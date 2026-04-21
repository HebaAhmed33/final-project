import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    "networkSecurity": { "score": 95, "label": "Good" },
    "accessCompliance": { "score": 100, "label": "Excellent" }
  });
}
