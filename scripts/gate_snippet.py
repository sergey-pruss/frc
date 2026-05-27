"""Inline site gate guard — imported by build/inject scripts."""

from __future__ import annotations

import re

GATE_GUARD_MARKER = "frc-gate-v1"
GATE_COOKIE_MAX_AGE = 31536000  # 365 days
PASS_HASH = "c6c2307ac025abfed680cb646bc38ca3c3d6e02662a0f2faa143dcff22268a49"

# Shared minified auth helpers (keep in sync with gate/index.html)
GATE_AUTH_CORE = (
    'var k="frc-gate-v1",h="'
    + PASS_HASH
    + '",g="/gate/",d="/seo/";'
    'function ga(){try{if(localStorage.getItem(k)===h)return!0}catch(e){}'
    'var c=document.cookie.split(";");'
    'for(var i=0;i<c.length;i++){var p=c[i].trim().split("=");'
    'if(p[0]===k)return decodeURIComponent(p.slice(1).join("="))===h}'
    'return!1}'
    'function sn(n){'
    'if(!n||n==="/"||n==="/index.html"||!n.startsWith("/")||n.startsWith("//")||n.indexOf("/gate")===0)return d;'
    'return n}'
)

GATE_GUARD_SCRIPT = f"""    <script>
(function(){{{GATE_AUTH_CORE}
if(location.pathname.indexOf("/gate")===0)return;
if(ga()){{if(location.pathname==="/"||location.pathname==="/index.html")location.replace(d);return}}
var n=location.pathname+location.search+location.hash;
location.replace(g+(n&&n!=="/"&&n!=="/index.html"?"?next="+encodeURIComponent(n):""));
}})();
</script>
"""

GATE_LOGIN_HEAD_SCRIPT = f"""    <script>
(function(){{{GATE_AUTH_CORE}
if(ga())location.replace(sn(new URLSearchParams(location.search).get("next")||""));
}})();
</script>
"""

EXTERNAL_GATE_RE = re.compile(
    r'\s*<script src="/assets/gate\.js\?v=[^"]+"></script>\n?',
    re.IGNORECASE,
)

INLINE_GATE_RE = re.compile(
    r'\s*<script>\n\(function\(\)\{[\s\S]*?frc-gate-v1[\s\S]*?\}\)\(\);\n</script>\n',
    re.IGNORECASE,
)
