import { NextResponse } from 'next/server';
export async function POST() {
  // Intentionally fail closed. Implement only after choosing an ad network whose
  // rewarded format permits this flow and verifying its signed server callback.
  return NextResponse.json({ granted: false, error: 'Rewarded-ad server verification is not configured.' }, { status: 501 });
}
