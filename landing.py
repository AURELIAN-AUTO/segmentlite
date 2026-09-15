import html
import os
from typing import Optional

def render_comparison_page(title_suffix: str = "", stripe_pro_url: Optional[str] = None) -> str:
    checkout_url = stripe_pro_url or os.getenv("STRIPE_LINK_SEGMENTLITE_PRO") or os.getenv("STRIPE_SEGMENTLITE_PRO_URL") or "https://buy.stripe.com/test_segmentlite_pro"
    html_body = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SegmentLite - The $29/mo Unbundled Alternative to Twilio Segment</title>
  <meta name="description" content="A high-throughput, lightweight event routing and webhook fan-out API for modern SaaS startups. Avoid Segment's $120/mo MTU price cliff.">
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              400: '#38bdf8',
              500: '#0ea5e9',
              600: '#0284c7'
            }
          }
        }
      }
    }
  </script>
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen selection:bg-brand-500 selection:text-white">

  <!-- Nav -->
  <header class="max-w-6xl mx-auto px-6 py-6 flex justify-between items-center border-b border-slate-800/60">
    <div class="flex items-center gap-3">
      <span class="text-2xl">⚡</span>
      <span class="font-extrabold tracking-tight text-xl bg-gradient-to-r from-sky-400 to-cyan-300 bg-clip-text text-transparent">SegmentLite</span>
      <span class="hidden sm:inline text-xs font-semibold px-2.5 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20">v1.0 Live</span>
    </div>
    <div class="flex items-center gap-4">
      <a href="/docs" class="text-sm font-medium text-slate-400 hover:text-white transition">Swagger Docs</a>
      <a href="https://rapidapi.com" target="_blank" class="text-sm font-bold bg-sky-500 hover:bg-sky-400 text-slate-950 px-4 py-2 rounded-lg transition shadow-lg shadow-sky-500/20">
        Get API Key on RapidAPI →
      </a>
    </div>
  </header>

  <!-- Hero -->
  <section class="max-w-4xl mx-auto px-6 pt-20 pb-16 text-center">
    <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-300 mb-8 shadow-inner">
      <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
      Tired of paying $120+/mo for simple event forwarding?
    </div>

    <h1 class="text-5xl sm:text-6xl font-black tracking-tight text-white mb-6 leading-tight">
      The Unbundled, <span class="bg-gradient-to-r from-sky-400 to-cyan-300 bg-clip-text text-transparent">$29/mo Alternative</span> to Segment.
    </h1>

    <p class="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
      Route your raw user events (<code class="text-sky-300">track</code> and <code class="text-sky-300">identify</code>) to Mixpanel, GA4, Slack alerts, and custom webhooks with sub-15ms latency. Zero MTU pricing cliffs.
    </p>

    <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
      <a href="#signup" class="w-full sm:w-auto px-8 py-4 rounded-xl font-bold text-slate-950 bg-sky-400 hover:bg-sky-300 transition shadow-xl shadow-sky-500/20 text-base">
        Start Free (1,000 events/mo) 🚀
      </a>
      <a href="/docs" class="w-full sm:w-auto px-8 py-4 rounded-xl font-semibold text-white bg-slate-900 hover:bg-slate-800 border border-slate-800 transition text-base">
        Explore Interactive API Docs
      </a>
    </div>
  </section>

  <!-- Direct Self-Service API Key Signup -->
  <section id="signup" class="max-w-3xl mx-auto px-6 py-6">
    <div class="bg-gradient-to-b from-slate-900 to-slate-950 border border-sky-500/30 rounded-2xl p-6 sm:p-10 shadow-2xl shadow-sky-500/10 relative overflow-hidden">
      <div class="absolute -top-24 -right-24 w-48 h-48 bg-sky-500/10 rounded-full blur-3xl pointer-events-none"></div>
      
      <div class="text-center mb-8">
        <span class="inline-block text-xs font-extrabold uppercase tracking-wider px-3 py-1 rounded-full bg-sky-500/20 text-sky-400 border border-sky-500/30 mb-3">
          Instant Self-Service Access
        </span>
        <h2 class="text-2xl sm:text-3xl font-extrabold text-white">Get Your Free API Key in 5 Seconds</h2>
        <p class="text-sm text-slate-400 mt-2">1,000 free events / month. No credit card required. Instant activation.</p>
      </div>

      <form id="signup-form" onsubmit="handleSignup(event)" class="flex flex-col sm:flex-row gap-3">
        <input 
          type="email" 
          id="signup-email" 
          placeholder="developer@startup.com" 
          required 
          class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-sky-400 transition"
        />
        <button 
          type="submit" 
          id="signup-btn"
          class="px-6 py-3.5 rounded-xl font-bold text-slate-950 bg-sky-400 hover:bg-sky-300 transition shadow-lg shadow-sky-500/20 text-sm whitespace-nowrap"
        >
          Claim API Key ⚡
        </button>
      </form>

      <!-- Results Container (Hidden Initially) -->
      <div id="signup-result" class="hidden mt-6 p-5 rounded-xl bg-slate-950 border border-slate-800">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            Key Activated (1,000 events/mo allocated)
          </span>
          <button type="button" onclick="copyApiKey()" class="text-xs text-sky-400 hover:text-sky-300 font-medium">
            Copy Key 📋
          </button>
        </div>
        <div class="bg-slate-900 px-4 py-3 rounded-lg border border-slate-800 font-mono text-xs sm:text-sm text-sky-300 break-all select-all" id="display-key">
        </div>
        
        <div class="mt-4">
          <div class="flex justify-between items-center mb-1">
            <span class="text-xs text-slate-400 font-semibold">Test Ingestion Now:</span>
            <button type="button" onclick="copySnippet()" class="text-xs text-slate-400 hover:text-white">Copy cURL</button>
          </div>
          <pre class="bg-slate-900 p-3 rounded-lg text-xs font-mono text-slate-300 overflow-x-auto border border-slate-800" id="display-curl"></pre>
        </div>

        <div class="mt-4 pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row justify-between items-center gap-3">
          <span class="text-xs text-slate-400">Need higher volume or priority workers?</span>
          <a href="https://buy.stripe.com/test_segmentlite_pro" target="_blank" class="text-xs font-bold text-sky-400 hover:text-sky-300 flex items-center gap-1">
            Upgrade to Starter Pro ($19/mo for 1M events) →
          </a>
        </div>
      </div>
    </div>
  </section>


  <!-- Comparison Table -->
  <section class="max-w-5xl mx-auto px-6 py-12">
    <div class="text-center mb-10">
      <h2 class="text-3xl font-extrabold text-white">Why Bootstrapped SaaS Drops Segment</h2>
      <p class="text-slate-400 mt-2">You don't need enterprise data governance. You just need event piping that works.</p>
    </div>

    <div class="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60 shadow-2xl backdrop-blur-sm">
      <table class="w-full text-left border-collapse text-sm">
        <thead>
          <tr class="border-b border-slate-800 bg-slate-900/90 text-slate-400 uppercase text-xs tracking-wider">
            <th class="p-5 font-semibold">Feature</th>
            <th class="p-5 font-semibold text-rose-400">Twilio Segment</th>
            <th class="p-5 font-semibold text-amber-400">RudderStack</th>
            <th class="p-5 font-bold text-sky-400 bg-sky-500/10">SegmentLite API ⚡</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800/60 text-slate-300">
          <tr>
            <td class="p-5 font-medium text-white">Starting Price</td>
            <td class="p-5 text-rose-400">$120 / month</td>
            <td class="p-5 text-amber-400">$349 / month</td>
            <td class="p-5 font-bold text-emerald-400 bg-sky-500/5">$0 Free / $29 Starter</td>
          </tr>
          <tr>
            <td class="p-5 font-medium text-white">Pricing Model</td>
            <td class="p-5">Confusing MTU cliffs</td>
            <td class="p-5">Event volume + Add-ons</td>
            <td class="p-5 font-bold text-emerald-400 bg-sky-500/5">Transparent per-event quota</td>
          </tr>
          <tr>
            <td class="p-5 font-medium text-white">Setup Friction</td>
            <td class="p-5">Complex multi-page SDKs</td>
            <td class="p-5">Self-hosting / Heavy setup</td>
            <td class="p-5 font-bold text-emerald-400 bg-sky-500/5">60-second REST API call</td>
          </tr>
          <tr>
            <td class="p-5 font-medium text-white">Fan-Out Speed</td>
            <td class="p-5">Variable</td>
            <td class="p-5">Fast</td>
            <td class="p-5 font-bold text-emerald-400 bg-sky-500/5">&lt; 15ms async background dispatch</td>
          </tr>
          <tr>
            <td class="p-5 font-medium text-white">Vendor Lock-In</td>
            <td class="p-5">High (Proprietary SDKs)</td>
            <td class="p-5">Moderate</td>
            <td class="p-5 font-bold text-emerald-400 bg-sky-500/5">Zero (Standard Webhooks & JSON)</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>

  <!-- Code Quickstart -->
  <section class="max-w-4xl mx-auto px-6 py-12">
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 shadow-xl">
      <div class="flex justify-between items-center mb-4">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-400">cURL Quickstart</span>
        <span class="text-xs text-sky-400 font-mono">POST /v1/track</span>
      </div>
      <pre class="bg-slate-950 p-4 rounded-xl text-xs sm:text-sm font-mono text-slate-300 overflow-x-auto border border-slate-800/80"><code>curl -X POST "https://segmentlite-api-dfru.fly.dev/v1/track" \\
  -H "Content-Type: application/json" \\
  -d '{
    "event": "User Signed Up",
    "user_id": "usr_10293",
    "properties": {
      "plan": "Pro",
      "referrer": "HackerNews"
    }
  }'</code></pre>
    </div>
  </section>

  <!-- Pricing Cards -->
  <section class="max-w-5xl mx-auto px-6 py-16">
    <div class="text-center mb-12">
      <h2 class="text-3xl font-extrabold text-white">Simple, Predictable Pricing</h2>
      <p class="text-slate-400 mt-2">No sudden 10x bills when your product launches on ProductHunt.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Free -->
      <div class="bg-slate-900/60 border border-slate-800 p-8 rounded-2xl flex flex-col justify-between">
        <div>
          <h3 class="text-lg font-bold text-white mb-1">Developer Free</h3>
          <p class="text-xs text-slate-400 mb-6">For testing & side projects.</p>
          <div class="text-4xl font-extrabold text-white mb-6">$0 <span class="text-xs font-normal text-slate-400">/mo</span></div>
          <ul class="space-y-3 text-sm text-slate-300 mb-8">
            <li class="flex items-center gap-2">✓ 1,000 events / month</li>
            <li class="flex items-center gap-2">✓ Up to 3 destinations</li>
            <li class="flex items-center gap-2">✓ Sub-15ms response latency</li>
          </ul>
        </div>
        <a href="#signup" class="w-full text-center py-3 rounded-xl font-semibold bg-slate-800 hover:bg-slate-700 text-white transition text-sm">
          Get Free Key Instantly →
        </a>
      </div>

      <!-- Starter -->
      <div class="bg-slate-900 border-2 border-sky-500/80 p-8 rounded-2xl flex flex-col justify-between relative shadow-2xl shadow-sky-500/10">
        <span class="absolute -top-3 left-1/2 -translate-x-1/2 bg-sky-500 text-slate-950 text-xs font-extrabold px-3 py-1 rounded-full uppercase tracking-wider">
          Most Popular
        </span>
        <div>
          <h3 class="text-lg font-bold text-white mb-1">Starter Pro</h3>
          <p class="text-xs text-slate-400 mb-6">For revenue-generating startups.</p>
          <div class="text-4xl font-extrabold text-white mb-6">$19 <span class="text-xs font-normal text-slate-400">/mo</span></div>
          <ul class="space-y-3 text-sm text-slate-300 mb-8">
            <li class="flex items-center gap-2">✓ <b>1,000,000</b> events / month</li>
            <li class="flex items-center gap-2">✓ Unlimited destinations</li>
            <li class="flex items-center gap-2">✓ Sub-15ms edge routing</li>
            <li class="flex items-center gap-2">✓ Priority queue workers</li>
          </ul>
        </div>
        <a href="{checkout_url}" target="_blank" class="w-full text-center py-3 rounded-xl font-bold bg-sky-400 hover:bg-sky-300 text-slate-950 transition text-sm shadow-lg shadow-sky-500/20">
          Subscribe with Stripe ($19/mo) 🚀
        </a>
      </div>

      <!-- Ultra -->
      <div class="bg-slate-900/60 border border-slate-800 p-8 rounded-2xl flex flex-col justify-between">
        <div>
          <h3 class="text-lg font-bold text-white mb-1">Business Scale</h3>
          <p class="text-xs text-slate-400 mb-6">For scaleups & high-volume apps.</p>
          <div class="text-4xl font-extrabold text-white mb-6">$79 <span class="text-xs font-normal text-slate-400">/mo</span></div>
          <ul class="space-y-3 text-sm text-slate-300 mb-8">
            <li class="flex items-center gap-2">✓ <b>10,000,000</b> events / month</li>
            <li class="flex items-center gap-2">✓ Unlimited destinations</li>
            <li class="flex items-center gap-2">✓ Dedicated queue workers</li>
            <li class="flex items-center gap-2">✓ Priority engineering SLA</li>
          </ul>
        </div>
        <a href="{checkout_url}" target="_blank" class="w-full text-center py-3 rounded-xl font-semibold bg-slate-800 hover:bg-slate-700 text-white transition text-sm">
          Subscribe with Stripe 🚀
        </a>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="max-w-6xl mx-auto px-6 py-8 border-t border-slate-800/60 text-center text-xs text-slate-500">
    <p>© 2026 SegmentLite. High-throughput event routing API. All trademarks belong to their respective owners.</p>
  </footer>

  <script>
    async function handleSignup(e) {
      e.preventDefault();
      const email = document.getElementById('signup-email').value;
      const btn = document.getElementById('signup-btn');
      btn.disabled = true;
      btn.innerText = 'Provisioning...';

      try {
        const res = await fetch('/v1/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email })
        });
        const data = await res.json();
        if (res.ok) {
          document.getElementById('display-key').innerText = data.api_key;
          document.getElementById('display-curl').innerText = data.curl_example;
          document.getElementById('signup-result').classList.remove('hidden');
          btn.innerText = 'Key Generated! ✓';
        } else {
          alert(data.detail || 'Signup failed. Please try again.');
          btn.innerText = 'Claim API Key ⚡';
        }
      } catch (err) {
        alert('Network error connecting to API.');
        btn.innerText = 'Claim API Key ⚡';
      } finally {
        btn.disabled = false;
      }
    }

    function copyApiKey() {
      const key = document.getElementById('display-key').innerText;
      navigator.clipboard.writeText(key);
      alert('API Key copied to clipboard!');
    }

    function copySnippet() {
      const snippet = document.getElementById('display-curl').innerText;
      navigator.clipboard.writeText(snippet);
      alert('cURL command copied to clipboard!');
    }
  </script>

</body>
</html>
"""
    return html_body.replace("{checkout_url}", checkout_url)

