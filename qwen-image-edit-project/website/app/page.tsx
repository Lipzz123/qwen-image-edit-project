'use client';
import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { Sparkles, ImagePlus, Cpu, ShieldCheck, LogIn, ExternalLink } from 'lucide-react';

type User = { email?: string } | null;
export default function Home() {
  const [user, setUser] = useState<User>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('Sign in to continue.');
  const [unlocked, setUnlocked] = useState(false);
  const notebookUrl = process.env.NEXT_PUBLIC_COLAB_NOTEBOOK_URL || '';
  const adsEnabled = process.env.NEXT_PUBLIC_REWARDED_ADS_ENABLED === 'true';

  useEffect(() => {
    if (!supabase) { setMessage('Supabase belum dikonfigurasi. Isi file .env.local terlebih dahulu.'); return; }
    supabase.auth.getUser().then(({ data }) => setUser(data.user ? { email: data.user.email } : null));
    const { data: listener } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ? { email: session.user.email } : null);
      setUnlocked(false);
    });
    return () => listener.subscription.unsubscribe();
  }, []);

  async function signIn() {
    if (!supabase) { setMessage('Konfigurasi Supabase belum lengkap.'); return; }
    setBusy(true);
    const { error } = await supabase.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: window.location.origin } });
    if (error) setMessage(error.message);
    setBusy(false);
  }
  async function signOut() { await supabase?.auth.signOut(); setUnlocked(false); }
  async function unlock() {
    if (!user) { setMessage('Login terlebih dahulu.'); return; }
    if (!adsEnabled) { setMessage('Rewarded ads belum dikonfigurasi. Akses notebook sengaja dikunci sampai provider iklan dan verifikasi server-side dipasang.'); return; }
    // Provider-specific rewarded-ad SDK must call a verified server callback.
    // Do not unlock based only on a client-side JavaScript event.
    setMessage('Integrasi provider iklan belum dipasang. Jangan membuka akses hanya dari callback browser.');
  }
  return <main className="wrap">
    <nav className="nav"><div className="brand">QWEN<span>·</span>STUDIO</div><div>{user ? <button className="pill" onClick={signOut}>{user.email} · Sign out</button> : <button className="pill" onClick={signIn} disabled={busy}><LogIn size={14} style={{verticalAlign:'middle',marginRight:7}}/>Sign in</button>}</div></nav>
    <section className="hero"><div className="eyebrow">AI IMAGE EDITING · POWERED BY QWEN</div><h1>Transform images<br/>with a simple prompt.</h1><p>Edit your images with Qwen Image Edit 2.1. The model runs in your own Google Colab session, using the GPU available to your account — no local installation required.</p><div className="actions"><button className="btn" onClick={unlock} disabled={!user || busy}>Unlock Colab access <ExternalLink size={16} style={{verticalAlign:'middle',marginLeft:6}}/></button><button className="btn secondary" onClick={()=>document.getElementById('how')?.scrollIntoView({behavior:'smooth'})}>How it works</button></div><div className="status">{message}</div></section>
    <section className="grid"><article className="card"><ImagePlus color="#c4b5fd"/><h3>Upload & describe</h3><p>Choose an image and describe the changes you want in natural language.</p></article><article className="card"><Cpu color="#c4b5fd"/><h3>Your Colab GPU</h3><p>Inference runs in the Colab runtime you start. This website does not provide or pay for GPU compute.</p></article><article className="card"><ShieldCheck color="#c4b5fd"/><h3>Transparent access</h3><p>Notebook access is granted only after the configured access flow is verified. Your Colab runtime remains under your control.</p></article></section>
    <section id="how" className="panel"><div className="eyebrow">GET STARTED</div><h2 style={{fontFamily:'Space Grotesk'}}>How it works</h2><ol className="muted" style={{lineHeight:2}}><li>Create an account or sign in with Google.</li><li>Complete the rewarded-ad step when a compliant ad provider is configured.</li><li>Open the public Colab notebook in Viewer mode.</li><li>Choose Runtime → Change runtime type → GPU.</li><li>Use File → Save a copy in Drive, then press Runtime → Run all.</li><li>Upload your image and enter your editing prompt in the notebook UI.</li></ol><p className="muted">A Viewer notebook is read-only. To run it, users need their own Drive copy. Viewer access does not hide source code or prevent copying code manually.</p>{notebookUrl && <a className="pill" href={notebookUrl} target="_blank" rel="noreferrer">Notebook link configured <ExternalLink size={13} style={{verticalAlign:'middle'}}/></a>}</section>
    <footer className="footer">Qwen Image Studio · Community project. Model and dependency licenses/terms apply. Google Colab availability and GPU quotas are controlled by Google.</footer>
  </main>;
}
