"""Inline site gate guard — imported by build/inject scripts."""

from __future__ import annotations

import re

GATE_GUARD_MARKER = "frc-gate-v1"
GATE_COOKIE_MAX_AGE = 31536000  # 365 days

GATE_GUARD_SCRIPT = """    <script>
(function(){var k="frc-gate-v1",h="c6c2307ac025abfed680cb646bc38ca3c3d6e02662a0f2faa143dcff22268a49",g="/gate/",d="/seo/",v="",c=document.cookie.split("; ");for(var i=0;i<c.length;i++){var p=c[i].split("=");if(p[0]===k){v=decodeURIComponent(p.slice(1).join("="));break}}if(v===h){if(location.pathname==="/"||location.pathname==="/index.html")location.replace(d);return}var p=location.pathname+location.search+location.hash;location.replace(g+(p&&p!=="/"&&p!=="/index.html"?"?next="+encodeURIComponent(p):""));})();
</script>
"""

GATE_LOGIN_COOKIE_SET = (
    'document.cookie=k+"="+h+"; Path=/; Max-Age=31536000; SameSite=Lax"'
    '+(location.protocol==="https:"?"; Secure":"")'
)

EXTERNAL_GATE_RE = re.compile(
    r'\s*<script src="/assets/gate\.js\?v=[^"]+"></script>\n?',
    re.IGNORECASE,
)

INLINE_GATE_RE = re.compile(
    r'\s*<script>\n\(function\(\)\{var k="frc-gate-v1"[\s\S]*?\}\)\(\);\n</script>\n',
    re.IGNORECASE,
)
