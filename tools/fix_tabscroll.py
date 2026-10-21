"""Clicking a tab scrolls to the top of that tab's section (just under the sticky tab bar).
The old version scrolled to the tab bar's own position, which is a no-op once the bar is stuck."""
import sys
OLD = """  function scrollToContentStart(){
    var nav = document.querySelector('.tabbar-outer');
    if(!nav){ window.scrollTo({top:0, behavior: reduce ? 'auto' : 'smooth'}); return; }
    var target = nav.getBoundingClientRect().top + window.pageYOffset;
    window.scrollTo({top: target, behavior: reduce ? 'auto' : 'smooth'});
  }"""
NEW = """  function scrollToContentStart(name){
    /* Scroll so the chosen section starts right under the sticky tab bar. */
    var nav = document.querySelector('.tabbar-outer');
    var panel = (name && name !== 'all' && document.getElementById('tab-' + name)) || document.querySelector('.tab-panel.active');
    var navH = nav ? nav.getBoundingClientRect().height : 0;
    var target = panel ? panel.getBoundingClientRect().top + window.pageYOffset - navH : 0;
    window.scrollTo({top: Math.max(0, target), behavior: reduce ? 'auto' : 'smooth'});
  }"""
for p in sys.argv[1:]:
    s = open(p, encoding='utf-8').read()
    if NEW in s: print(p, 'already'); continue
    if s.count(OLD) != 1 or s.count('scrollToContentStart();') != 1:
        print(p, 'SKIP pattern mismatch'); continue
    s = s.replace(OLD, NEW).replace('scrollToContentStart();', 'scrollToContentStart(name);')
    open(p, 'w', encoding='utf-8').write(s); print(p, 'ok')
