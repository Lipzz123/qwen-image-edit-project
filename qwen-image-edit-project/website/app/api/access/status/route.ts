import { NextResponse } from 'next/server';
export async function GET() {
  // TODO: check authenticated Supabase user + server-side access_grants table.
  // Never trust a browser-provided `watched=true` flag.
  return NextResponse.json({ configured: false, unlocked: false, reason: 'Rewarded-ad provider and grant storage are not configured.' }, { status: 503 });
}
