# Website starter — Qwen Image Studio

Next.js frontend starter with Supabase Google OAuth. It is not a production-ready rewarded-ad implementation yet.

## Run locally

```bash
cd website
cp .env.example .env.local
npm install
npm run dev
```

Set the following in `.env.local`:

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_COLAB_NOTEBOOK_URL`
- `NEXT_PUBLIC_REWARDED_ADS_ENABLED=false` until the ad integration is complete
- `AD_PROVIDER_WEBHOOK_SECRET` as a server-only secret when implementing a provider callback

In Supabase, create a project, enable Google as an OAuth provider, configure the Google OAuth credentials, and add your local/deployed site URL to Supabase Auth redirect URL allow-list.

## Rewarded ad integration — intentionally unfinished

The starter does not claim that an ad has been watched. `app/api/access/grant/route.ts` fails closed. To finish this safely:

1. Choose an ad network/format whose written policies permit a rewarded ad to unlock this type of content/access.
2. Implement the provider SDK in the browser.
3. Configure the provider's server-to-server callback/postback.
4. Verify the provider signature, event ID, reward status, placement, and user/session mapping on the server.
5. Store a one-time access grant in a database with expiry and replay protection.
6. Only then expose a server-checked “Open Colab” action.

Do not treat a browser event, query parameter, or localStorage flag as proof that an ad was completed. Do not require users to click ads or interact with ordinary ads; follow the ad provider's rewarded-ad policy and consent requirements. Google AdSense rewarded/Offerwall products have their own eligibility, consent, and implementation requirements; ordinary ads cannot simply be forced as a condition of access.

## Important: public Colab link is shareable

Once a user sees the public notebook URL, they can bookmark or share it. A public GitHub notebook is also directly discoverable. Therefore this access gate is a user journey/monetization layer, not an enforceable security boundary. Viewer sharing only prevents edits to the original Drive notebook; it does not hide code or reliably prevent copying.

## Production checklist

- [ ] Configure Supabase Google OAuth and production redirect URLs.
- [ ] Add server-side session validation and database-backed one-time access grants.
- [ ] Select and integrate a compliant rewarded-ad provider.
- [ ] Verify signed provider callbacks server-side; reject replayed events.
- [ ] Add rate limits, abuse monitoring, privacy notice, terms, and deletion/contact process.
- [ ] Set `NEXT_PUBLIC_COLAB_NOTEBOOK_URL` to the final Colab URL.
- [ ] Test mobile layout and OAuth callback on deployed domain.
- [ ] Review Google Colab terms and model/dependency licenses for the intended public/commercial use.
