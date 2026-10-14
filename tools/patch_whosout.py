#!/usr/bin/env python3
"""Make the Who's Out / Birthdays block read whosout.json live.
Touches ONLY the <script id="eaw-whos-out-wire"> block. Every anchor must match exactly once."""
import sys,re
if len(sys.argv)<3:
    sys.exit("usage: patch_whosout.py IN.html OUT.html [FEED_URL]")
src,dst=sys.argv[1],sys.argv[2]
FEED=sys.argv[3] if len(sys.argv)>3 else "https://raw.githubusercontent.com/kristanseaw-ux/eaw-portal-data/main/whosout.json"
t=open(src,encoding='utf-8').read()
i=t.index('<script id="eaw-whos-out-wire">'); j=t.index('</script>',i)+9
assert t.count('<script id="eaw-whos-out-wire">')==1
b=t[i:j]; orig=b
def sub(old,new,count=1):
    global b
    assert b.count(old)==count,(old[:60],b.count(old))
    b=b.replace(old,new)

sub("(function () {\n  'use strict';","window.eawWhosOutRender = function (feed) {\n  'use strict';")
m=re.search(r"\n  var EVENTS = \[\[.*?\]\];\n",b,re.S); assert m
b=b[:m.end()]+"  if (feed && feed.length) EVENTS = feed;   // live feed overrides the baked-in snapshot\n"+b[m.end():]
sub("if(/\\bOFF\\b|OUT OF TOWN|VACAT|VACAY|\\bPTO\\b/i.test(s)) return 'timeoff';",
    "if(/\\bOFF\\b|\\bOUT\\b|OUT OF TOWN|VACAT|VACAY|\\bPTO\\b/i.test(s)) return 'timeoff';")
sub("var m=s.match(/^(.*?)\\s*\\b(?:OFF|B\\s?DAY|BIRTHDAY)\\b\\s*[-–—:]?\\s*(.*)$/i);",
    "var m=s.match(/^(.*?)\\s*\\b(?:OFF|B\\s?DAY|BIRTHDAY|OUT(?!\\s+of\\s+town))\\b\\s*[-–—:]?\\s*(.*)$/i);")
sub("st.getDay()===6 && st.getHours()===8","st.getDay()===6 && st.getHours()>=7 && st.getHours()<=8")
tail="})();\n</script>"
assert b.endswith(tail)
b=b[:-len(tail)]+"""};
  window.eawWhosOutRender();   // paint at once from the baked-in snapshot (same as before)

  /* LIVE FEED — written by the Who's Out updater from the Outlook calendar "EAW Time Off Requests".
     If it can't be reached the snapshot above stays on screen. Keep the cache-buster. */
  (function(){
    var FEED='"""+FEED+"""';
    function load(){
      fetch(FEED+'?t='+Date.now(),{cache:'no-store'})
        .then(function(r){return r.ok?r.json():null;})
        .then(function(d){ if(d&&d.events&&d.events.length) window.eawWhosOutRender(d.events); })
        .catch(function(){ /* feed unreachable - keep snapshot */ });
    }
    if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',load); else load();
  })();
</script>"""
out=t[:i]+b+t[j:]
assert out[:i]==t[:i] and out[i+len(b):]==t[j:]   # nothing outside the block changed
open(dst,'w',encoding='utf-8').write(out)
print('patched; block',len(orig),'->',len(b))
