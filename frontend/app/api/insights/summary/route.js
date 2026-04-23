import { NextResponse } from "next/server";

export async function GET() {
  // Mock data for the Security Overview
  return NextResponse.json({
    securityScore: 85,
    riskLevel: "Medium",
    compliancePercent: 92,
  });
}
