/* =====================================================================
   CLINICBRAIN — Premium template interactions (shared)
   Mirrors the Rosmarakis premium build: reveal-on-scroll, sticky header,
   scroll-spy, mobile drawer, services accordion, count-up, magnetic
   buttons, ripple, cursor glow, live opening-hours, content lock.
   Opening hours can be overridden per page via window.CLINIC_SCHEDULE.
   ===================================================================== */
(function(){
  "use strict";
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- year ---- */
  var y = document.getElementById('year'); if(y) y.textContent = new Date().getFullYear();

  /* ---- split-letter hero stagger ---- */
  if(!reduce){
    document.querySelectorAll('#heroH1 .word i').forEach(function(el,i){
      el.style.animationDelay = (0.15 + i*0.09) + 's';
    });
  }

  /* ---- staggered reveal ---- */
  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }});
  }, {threshold:.14, rootMargin:'0px 0px -8% 0px'});
  document.querySelectorAll('.reveal').forEach(function(el){ io.observe(el); });
  document.querySelectorAll('.exam-grid, .stats-grid, .cred-list, .svc-list').forEach(function(g){
    g.querySelectorAll('.reveal, .exam').forEach(function(el,i){ el.style.transitionDelay = (i*0.07)+'s'; });
  });

  /* ---- scroll progress + header + back to top ---- */
  var progress = document.getElementById('progress'),
      topbar = document.getElementById('topbar'),
      toTop = document.getElementById('toTop');
  function onScroll(){
    var st = window.scrollY || document.documentElement.scrollTop;
    var h = document.documentElement.scrollHeight - window.innerHeight;
    if(progress) progress.style.width = (h>0 ? st/h*100 : 0) + '%';
    if(topbar) topbar.classList.toggle('scrolled', st>30);
    if(toTop) toTop.classList.toggle('show', st>520);
  }
  window.addEventListener('scroll', onScroll, {passive:true}); onScroll();
  if(toTop) toTop.addEventListener('click', function(){ window.scrollTo({top:0, behavior: reduce?'auto':'smooth'}); });

  /* ---- scroll-spy ---- */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.nav-links a'));
  var secs = navLinks.map(function(a){ return {a:a, sec:document.querySelector(a.getAttribute('href'))}; })
                     .filter(function(o){ return o.sec; });
  if(secs.length){
    var spy = new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(e.isIntersecting){
          navLinks.forEach(function(a){ a.classList.remove('active'); });
          var m = secs.find(function(o){ return o.sec===e.target; });
          if(m) m.a.classList.add('active');
        }
      });
    }, {rootMargin:'-45% 0px -50% 0px'});
    secs.forEach(function(o){ spy.observe(o.sec); });
  }

  /* ---- mobile drawer ---- */
  var ham = document.getElementById('hamburger'), ov = document.getElementById('overlay');
  function toggleMenu(){ document.body.classList.toggle('menu-open'); }
  if(ham) ham.addEventListener('click', toggleMenu);
  if(ov) ov.addEventListener('click', toggleMenu);
  document.querySelectorAll('#drawer a').forEach(function(a){ a.addEventListener('click', function(){ document.body.classList.remove('menu-open'); }); });

  /* ---- services accordion ---- */
  document.querySelectorAll('#svcList .svc-row').forEach(function(row){
    var head = row.querySelector('.svc-head');
    if(head) head.addEventListener('click', function(){
      var open = row.classList.contains('open');
      document.querySelectorAll('#svcList .svc-row').forEach(function(r){ r.classList.remove('open'); });
      if(!open) row.classList.add('open');
    });
  });

  /* ---- count-up ---- */
  function countUp(el){
    var target = parseInt(el.getAttribute('data-count'),10);
    var suffix = el.getAttribute('data-suffix')||'';
    if(reduce){ el.textContent = target.toLocaleString('el-GR')+suffix; return; }
    var dur=1400, t0=performance.now();
    requestAnimationFrame(function step(now){
      var p = Math.min((now-t0)/dur,1);
      var v = Math.round((1-Math.pow(1-p,3))*target);
      el.textContent = v.toLocaleString('el-GR')+suffix;
      if(p<1) requestAnimationFrame(step);
    });
  }
  var cObs = new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ countUp(e.target); cObs.unobserve(e.target); }});
  }, {threshold:.6});
  document.querySelectorAll('[data-count]').forEach(function(el){ cObs.observe(el); });

  /* ---- magnetic buttons ---- */
  if(!reduce && window.matchMedia('(pointer:fine)').matches){
    document.querySelectorAll('[data-magnetic]').forEach(function(btn){
      btn.addEventListener('mousemove', function(e){
        var r = btn.getBoundingClientRect();
        var x = e.clientX - r.left - r.width/2;
        var y = e.clientY - r.top - r.height/2;
        btn.style.transform = 'translate('+(x*0.25)+'px,'+(y*0.35)+'px)';
      });
      btn.addEventListener('mouseleave', function(){ btn.style.transform=''; });
    });
  }

  /* ---- ripple ---- */
  document.querySelectorAll('.btn').forEach(function(b){
    b.addEventListener('click', function(ev){
      if(reduce) return;
      var r=this.getBoundingClientRect(), s=Math.max(r.width,r.height);
      var sp=document.createElement('span'); sp.className='ripple';
      sp.style.width=sp.style.height=s+'px';
      sp.style.left=(ev.clientX-r.left-s/2)+'px';
      sp.style.top=(ev.clientY-r.top-s/2)+'px';
      this.appendChild(sp); setTimeout(function(){ sp.remove(); },600);
    });
  });

  /* ---- cursor glow ---- */
  var glow = document.getElementById('glow');
  if(glow && !reduce && window.matchMedia('(pointer:fine)').matches){
    var gx=0,gy=0,cx=0,cy=0,raf;
    window.addEventListener('mousemove', function(e){ gx=e.clientX; gy=e.clientY; glow.style.opacity='1';
      if(!raf) raf=requestAnimationFrame(loop); });
    function loop(){ cx+=(gx-cx)*0.12; cy+=(gy-cy)*0.12;
      glow.style.transform='translate('+cx+'px,'+cy+'px) translate(-50%,-50%)';
      raf=requestAnimationFrame(loop); }
  }

  /* ---- marquee duplication for seamless loop ---- */
  var mq = document.getElementById('marquee');
  if(mq) mq.innerHTML += mq.innerHTML;

  /* ===== OPENING HOURS LOGIC (live) ===== */
  // schedule[day] = array of [startMin, endMin]; day 0 = Sunday
  var schedule = window.CLINIC_SCHEDULE || {
    1:[[540,840],[1020,1260]], // Mon 9-14, 17-21
    2:[[540,840],[1020,1260]], // Tue
    3:[[1020,1260]],           // Wed 17-21
    4:[[540,840],[1020,1260]], // Thu
    5:[[540,840]],             // Fri 9-14
    6:[],                      // Sat
    0:[]                       // Sun
  };
  var dayNamesGen = ['Κυριακή','Δευτέρα','Τρίτη','Τετάρτη','Πέμπτη','Παρασκευή','Σάββατο'];
  function fmt(m){ var h=Math.floor(m/60), mm=m%60; return (h<10?'0':'')+h+':'+(mm<10?'0':'')+mm; }

  function nextOpening(now, day, mins){
    for(var i=0;i<7;i++){
      var d=(day+i)%7, slots=schedule[d];
      for(var j=0;j<slots.length;j++){
        if(i===0 && slots[j][0]<=mins) continue;
        return {day:d, start:slots[j][0], same:i===0};
      }
    }
    return null;
  }

  function refreshStatus(){
    var now=new Date(), day=now.getDay(), mins=now.getHours()*60+now.getMinutes();
    var slots=schedule[day], openNow=false, closesAt=null;
    for(var i=0;i<slots.length;i++){ if(mins>=slots[i][0] && mins<slots[i][1]){ openNow=true; closesAt=slots[i][1]; break; } }

    var statusText, subText;
    if(openNow){
      statusText='Ανοιχτά τώρα';
      subText='Κλείνει στις '+fmt(closesAt);
    } else {
      statusText='Κλειστά τώρα';
      var nx=nextOpening(now, day, mins);
      if(nx){
        var when = nx.same ? 'σήμερα' : (nx.day===(day+1)%7 ? 'αύριο' : dayNamesGen[nx.day]);
        subText='Ανοίγει '+when+' στις '+fmt(nx.start);
      } else { subText='Επικοινωνήστε για ραντεβού'; }
    }

    var dotA=document.getElementById('dotAside'); if(dotA) dotA.classList.toggle('on', openNow);
    var lblA=document.getElementById('statusAside'); if(lblA) lblA.textContent = statusText;
    var sub=document.getElementById('subAside'); if(sub) sub.textContent=subText;

    // today highlight in table
    document.querySelectorAll('#hoursTable .hrow').forEach(function(r){
      r.classList.toggle('today', parseInt(r.getAttribute('data-day'),10)===day);
    });

    // contact today line
    var ct=document.getElementById('contactToday'), ch=document.getElementById('contactHours');
    if(ct&&ch){
      ct.textContent = (openNow?'Ανοιχτά σήμερα':'Σήμερα: '+dayNamesGen[day]);
      var todays=schedule[day];
      ch.textContent = todays.length ? todays.map(function(s){return fmt(s[0])+'–'+fmt(s[1]);}).join(' · ') : 'Κλειστά — δείτε ωράριο';
    }
  }

  function tickClock(){
    var now=new Date();
    var lc=document.getElementById('liveClock'), ld=document.getElementById('liveDate');
    if(lc) lc.textContent = now.toLocaleTimeString('el-GR',{hour:'2-digit',minute:'2-digit'});
    if(ld) ld.textContent = now.toLocaleDateString('el-GR',{weekday:'long',day:'numeric',month:'long'});
  }
  refreshStatus(); tickClock();
  setInterval(tickClock,1000);
  setInterval(refreshStatus,30000);

  /* ---- content lock: right-click, selection, copy/paste, source shortcuts ---- */
  var block = function(e){ e.preventDefault(); e.stopPropagation(); return false; };
  document.addEventListener('contextmenu', block);
  ['copy','cut','paste','selectstart','dragstart'].forEach(function(ev){
    document.addEventListener(ev, block);
  });
  document.addEventListener('keydown', function(e){
    var k = (e.key || '').toLowerCase();
    if(k === 'f12') return block(e);
    if((e.ctrlKey || e.metaKey) && !e.shiftKey && ['c','x','v','u','s','p','a'].indexOf(k) > -1) return block(e);
    if((e.ctrlKey || e.metaKey) && e.shiftKey && ['i','j','c'].indexOf(k) > -1) return block(e);
  });
})();
