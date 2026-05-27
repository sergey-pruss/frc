"""Inline site gate guard — imported by build/inject scripts."""

from __future__ import annotations

import re

GATE_GUARD_MARKER = "frc-gate-v1"

GATE_GUARD_SCRIPT = """    <script>
(function(){var k="frc-gate-v1",h="c6c2307ac025abfed680cb646bc38ca3c3d6e02662a0f2faa143dcff22268a49",g="/gate/",d="/seo/";try{if(sessionStorage.getItem(k)===h){if(location.pathname==="/"||location.pathname==="/index.html")location.replace(d);return}}catch(e){}var p=location.pathname+location.search+location.hash;location.replace(g+(p&&p!=="/"&&p!=="/index.html"?"?next="+encodeURIComponent(p):""));})();
</script>
"""

EXTERNAL_GATE_RE = re.compile(
    r'\s*<script src="/assets/gate\.js\?v=[^"]+"></script>\n?',
    re.IGNORECASE,
)
