/* JAH GUIDE (2026-10-04 TOUR-FIX standard):
   1) First-visit WELCOME overlay (localStorage flag jah-tour-seen-calculator):
      centered modal, 5 plain-language steps, ONE "OK — Got it" button.
      NO auto-scroll, NO spotlight ring, NO section jumps — the page stays put.
   2) Permanent "? Guide" button in the sticky tab bar re-opens the welcome overlay;
      the overlay has a "Full how-to guide" button for the full feature guide below.
   ES5-safe, additive, theme untouched (reuses --cy/--panel/--line/--txt vars). */
(function(){
"use strict";
var LS_KEY="jah-tour-seen-calculator";
var CY="#35e0ff";

/* ---------------- tour steps: all target real DOM ids ---------------- */
var STEPS=[
 {tab:"basic",sel:"#tabbar",title:"1 · The 9 mode tabs",
  what:"WHAT: the sticky mode bar at the top of the page.",
  does:"WHAT IT DOES: switches between Basic, Scientific, Ask Anything, Paradox Check, Projection, Simulate, Lab, Equations, and Record — each is its own tool.",
  how:"HOW: tap a tab. Every tab has its own link too (?tab=sci, ?tab=lab …) so you can bookmark or share the exact tool."},
 {tab:"basic",sel:"#p-basic",title:"2 · Basic calculator",
  what:"WHAT: the Basic panel — type any expression and calculate.",
  does:"WHAT IT DOES: a hand-written expression parser (never eval) evaluates it and shows its work step by step, wrapped in an INPUT / METHOD / OUTPUT / STATUS panel.",
  how:"HOW: type e.g. (12 + 8) * 3 / 4 - 2^3 and hit Calculate. M+ / M- store and recall values, MR inserts, MC clears. Fun fact: 0^0 is defined here as 1, and the page says so."},
 {tab:"sci",sel:"#p-sci",title:"3 · Scientific tab",
  what:"WHAT: the Scientific panel — trig, logs, powers, plus two solvers and a converter.",
  does:"WHAT IT DOES: DEG/RAD toggle for trig, quadratic and cubic equation solvers (real and complex roots shown honestly), and a unit converter for length, mass, temperature, data, and time.",
  how:"HOW: tap a function button to insert it, set DEG or RAD, type coefficients for the solvers (e.g. a=1 b=-3 c=2), pick a category and units for conversions."},
 {tab:"ask",sel:"#p-ask",title:"4 · Ask Anything",
  what:"WHAT: the Ask Anything panel — ask in plain words or type math.",
  does:"WHAT IT DOES: computes math inside your question, gives one clear JAH ANSWER for known topics, says FACT NOT AVAILABLE when it has no stored definition (never invents one), and runs a ten-lens analysis with a fusion verdict.",
  how:"HOW: try 'What is gravity?', '15% of 240', or 'bridges vs tunnels'. Tap 🔊 Read answer aloud to hear it. It computes from your words — it does not browse the web."},
 {tab:"paradox",sel:"#p-paradox",title:"5 · Paradox Check",
  what:"WHAT: the Paradox Check panel — the paradox-immune engine.",
  does:"WHAT IT DOES: a three-gate engine checks your statement: Gate A tests it is complete, well-formed English; Gate B matches known traps (liar, barber, Russell, Zeno, omnipotence, and more); Gate C catches self-reference and direct contradiction.",
  how:"HOW: type a statement like \"This statement is false\" and hit Check. You get the detected condition, the reason, and the resolution — e.g. it now catches the omnipotence puzzle even with misspellings."},
 {tab:"project",sel:"#p-project",title:"6 · Projection engine",
  what:"WHAT: the Projection panel — paste a number series, get a forecast.",
  does:"WHAT IT DOES: fits both a straight-line and an exponential curve, reports R^2 for each, charts everything, and forecasts your chosen number of steps ahead with the better fit.",
  how:"HOW: paste one number per line (at least 3), set forecast steps, run it. Remember the warning: forecasts extrapolate the fitted curve — they are not predictions."},
 {tab:"sim",sel:"#p-sim",title:"7 · Simulation deck",
  what:"WHAT: the Simulate panel — four live simulations that run on your device.",
  does:"WHAT IT DOES: Game of Life (tap cells to seed, then run), Monte Carlo pi (dart throws), Dice probability lab (histogram), and Random Walk. All are seeded, so the same seed reproduces the same run.",
  how:"HOW: Game of Life — tap the grid, hit Run, drag the speed slider. For the others, pick a seed, run, and use Reproduce to replay the exact same experiment. Nothing leaves your device."},
 {tab:"lab",sel:"#p-lab",title:"8 · Virtual lab bench",
  what:"WHAT: the Lab panel — four real experiments, simulated.",
  does:"WHAT IT DOES: pendulum period, projectile motion, Ohm's law, and ideal gas. Move the sliders and the readings update live with the formulas shown. Record reading saves each one to your lab notebook.",
  how:"HOW: drag sliders, tap Record reading after each, then Export CSV to download your data. All readings are simulated — never physical measurements."},
 {tab:"eq",sel:"#p-eq",title:"9 · Equation archive",
  what:"WHAT: the Equations panel — the official JAH-EQ solved-equation archive, marching to 1,000,000.",
  does:"WHAT IT DOES: every equation solved once, published as a permanent JAH-EQ record, then retrieved. The Finder reads your plain-words description and brings the five closest records; search and 12 category filters cover the rest.",
  how:"HOW: type in the Finder ('Describe what you're looking for…') or search for words like 'quadratic' or an ID like JAH-EQ-00000001. Tap any record to open its steps."},
 {tab:"rec",sel:"#p-rec",title:"10 · Solve record",
  what:"WHAT: the Record panel — everything you solve is saved here.",
  does:"WHAT IT DOES: keeps every solve (up to 500) in this browser only — nothing uploaded. Read it aloud, copy it, download it as .txt, or clear it.",
  how:"HOW: solve anything on any tab and it appears here automatically. Read aloud / Copy record / Download .txt / Clear are the four buttons at the top."},
 {tab:"basic",sel:"#p-basic .actions",title:"11 · Read, copy, download",
  what:"WHAT: the action row under every result on every tab.",
  does:"WHAT IT DOES: 🔊 reads the result aloud with a tiered voice chain (your device voice, then ResponsiveVoice, then Google) with speed control; ⧉ copies; ⤓ downloads the result as a .txt file. Send-to links push the result to the Dictionary, JAH Wiki, or Spec Catalog.",
  how:"HOW: get any result, then tap 🔊, ⧉, or ⤓ in the row beneath it. ⏹ stops the voice. Red Reset this tool buttons clear a tool without touching your solve record."}
];

/* ---------------- guide content: every user-facing feature ---------------- */
var GUIDE=[
 {h:"The 9 mode tabs",p:["WHAT IT DOES: Basic, Scientific, Ask Anything, Paradox Check, Projection, Simulate, Lab, Equations, Record — each tab is a separate tool with its own inputs and results.","HOW TO USE: tap a tab in the sticky bar. Deep links: ?tab=sci, ?tab=lab, etc. — bookmark or share the exact tool. Enter key runs the tool from any of its inputs."]},
 {h:"Basic calculator",p:["WHAT IT DOES: evaluates any typed expression with a hand-written parser (no eval, no black box) and shows each evaluation step. Results are labeled INPUT / METHOD / OUTPUT / STATUS.","HOW TO USE: type e.g. (12 + 8) * 3 / 4 - 2^3 and hit Calculate. Function buttons insert ( ) + - x / % ^ pi sqrt. M+ / M- store values, MR inserts the stored value, MC clears it. Note: 0^0 is defined here as 1 (IEEE 754 convention), and the result says so."]},
 {h:"Scientific tab",p:["WHAT IT DOES: trig functions with a DEG/RAD toggle, logs, powers, roots, factorial, plus a quadratic solver (real and complex roots), a cubic solver, and a unit converter (length, mass, temperature, data, time).","HOW TO USE: tap function buttons to insert them; switch DEG or RAD before trig. Type solver coefficients (e.g. a=1 b=-3 c=2) and hit Solve; pick a converter category, type a value, choose from/to units, and Convert."]},
 {h:"Ask Anything",p:["WHAT IT DOES: answers plain-words questions and math. Math inside a question is computed. Known topics get one clear JAH ANSWER; unknown topics get an honest FACT NOT AVAILABLE — nothing is invented. Also offers comparisons, Fermi estimation for quantity questions, a ten-lens analysis, and a fusion verdict.","HOW TO USE: try 'What is gravity?', '15% of 240', or 'bridges vs tunnels'. Tap 🔊 Read answer aloud. Show ten-lens analysis expands the detail. Note: it computes from your words — it does not browse the web."]},
 {h:"Paradox Check",p:["WHAT IT DOES: a three-gate paradox engine. Gate A checks the statement is complete, well-formed English (too short, unknown words with a spelling suggestion, or unfinished sentences are flagged — never called 'stable'). Gate B matches known traps: liar, barber, Russell's sets, sorites, unexpected hanging, omnipotence, irresistible force, Pinocchio, grandfather, ship of Theseus, Zeno — typo-tolerant. Gate C catches self-reference and direct contradiction.","HOW TO USE: type a statement like \"This statement is false\" and hit Check. Read the detected condition, the reason, and the resolution."]},
 {h:"Projection engine",p:["WHAT IT DOES: pastes a number series, fits linear AND exponential curves, reports R^2 for each, charts it, and forecasts your chosen steps ahead using the better fit. It refuses exponential fits on constant, zero, or negative data — and says why.","HOW TO USE: paste numbers one per line (at least 3), set forecast steps (1–50), run it. Warning printed on every forecast: forecasts extrapolate the fitted curve — they are not predictions."]},
 {h:"Simulation deck",p:["WHAT IT DOES: four live on-device simulations. Game of Life: 36x24 toroidal grid, standard Conway B3/S23 rules, tap cells to seed. Monte Carlo pi: seeded dart throws estimate pi. Dice probability lab: histograms of n-dice rolls. Random walk: 500-step walk with distance readout. All seeded — the same seed reproduces the same run.","HOW TO USE: Game of Life — tap the grid (or focus it, arrow keys + Space/Enter), Run/Pause, Random seed, speed slider. Others — set a seed, run, and use Reproduce to replay exactly. Nothing leaves your device."]},
 {h:"Virtual lab bench",p:["WHAT IT DOES: four simulated experiments with live sliders and the governing formula shown: pendulum period T=2pi*sqrt(L/g), projectile motion (range, height, time + chart), Ohm's law (current and power), ideal gas (P=nRT/V). Record reading saves each reading to your lab notebook.","HOW TO USE: drag sliders, tap Record reading, then Export CSV to download your data or Clear notebook to wipe it. All readings are simulated — never physical measurements."]},
 {h:"Equation archive (JAH-EQ)",p:["WHAT IT DOES: the official solved-equation archive, marching to 1,000,000. Every equation solved once, published as a JAH-EQ record, then retrieved. The Finder takes a plain-words description and returns the five closest records; the search box and 12 category filters (Linear, Quadratic, Systems, Trig, Powers & roots, Logarithms, Exponentials, Evaluate, Percent, Derivatives, Integrals, Geometry) cover the rest.","HOW TO USE: use the Finder ('Describe what you're looking for…'), search for words ('pyramid') or IDs (JAH-EQ-00000001), or tap category pills. Tap a record to open its steps. Deep links: ?eq=JAH-EQ-00000001, ?tab=eq&type=quadratic. Full CSV download in the footer."]},
 {h:"Solve record",p:["WHAT IT DOES: every solve on every tab is recorded automatically (up to 500), stored in this browser only — nothing uploaded, survives refresh, lost if browser data is cleared, not shared across devices. Each entry gets a deterministic JAH-SOLVE ID.","HOW TO USE: open the Record tab; Read aloud, Copy record, Download .txt, or Clear. Red Reset this tool buttons on each tab clear that tool only — never the record."]},
 {h:"Read aloud, copy, download — on every tab",p:["WHAT IT DOES: under each result, 🔊 reads it aloud through a tiered voice chain (your device voice first, then ResponsiveVoice, then two Google TTS hosts) with a 0.8x–2x speed selector; ⏹ stops the voice; ⧉ copies the result; ⤓ downloads it as a .txt file. Send-to links push the result to the Dictionary, JAH Wiki, or Spec Catalog.","HOW TO USE: solve anything, then use the row under the result. Reading speed: the small dropdown next to ⏹."]},
 {h:"Errors and validation",p:["WHAT IT DOES: mistakes get honest, specific error states — syntax errors, missing coefficients, division by zero, 0/0, log of zero, domain errors — each labeled with what happened, why, a valid example, and how to recover. Empty fields show a red inline error that clears as you type.","HOW TO USE: read the error box — it tells you exactly what to fix. No result is ever a guess."]},
 {h:"Also handy",p:["The status line under the title shows the engine self-test result, definition count, archive size, and record mode.","The circle button at the bottom-right toggles dark mode.","The footer has Data & methodology, the full equation catalog CSV, and the sitemap."]}
];

function _jps(){if(typeof JAHProfile!=="undefined"&&JAHProfile&&JAHProfile.store)return JAHProfile.store;return{get:function(k){try{return localStorage.getItem(k)}catch(e){return null}},set:function(k,v){try{localStorage.setItem(k,v)}catch(e){}}}}
function seen(){try{return _jps().get(LS_KEY)==="1"}catch(e){return true}}
function markSeen(){try{_jps().set(LS_KEY,"1")}catch(e){}}
function el(tag,cls,html){var d=document.createElement(tag);if(cls)d.className=cls;if(html!=null)d.innerHTML=html;return d}
var BASECSS={
 position:"fixed",zIndex:100000,fontFamily:"Arial,Helvetica,sans-serif",
 background:"var(--panel,#131b29)",color:"var(--txt,#dbe7f5)",
 border:"2px solid "+CY,borderRadius:"10px",
 boxShadow:"0 6px 24px rgba(0,0,0,.6)",padding:"14px 16px"
};
function style(d,obj){for(var k in obj)d.style[k]=obj[k];return d}
function bigBtn(t,primary){var b=el("button",null,t);
 style(b,{minHeight:"48px",minWidth:"48px",fontSize:"1.05em",padding:"12px 22px",
  borderRadius:"8px",cursor:"pointer",margin:"8px 8px 0 0",fontFamily:"Arial,Helvetica,sans-serif",
  border:primary?"none":"1px solid "+CY,
  background:primary?CY:"#1c2940",color:primary?"#04121a":"var(--txt,#dbe7f5)",
  fontWeight:primary?"bold":"normal"});
 return b}

/* ---------------- first-visit WELCOME overlay ---------------- */
var WELCOME_STEPS=[
 "<b>Pick a mode tab.</b> The sticky bar at the top has 9 tools: Basic, Scientific, Ask Anything, Paradox Check, Projection, Simulate, Lab, Equations, and Record.",
 "<b>Type and calculate.</b> In Basic, type any expression and hit Calculate — it shows its work step by step.",
 "<b>Ask, or check for paradoxes.</b> Ask Anything answers plain-words questions; Paradox Check tests a statement like \"This statement is false\" through the three-gate engine.",
 "<b>Explore the archives.</b> The Equations tab holds the JAH-EQ solved-equation archive; the Record tab keeps every solve — on this device only.",
 "<b>Read, copy, download.</b> Every result has read-aloud, copy, and .txt download buttons in the row beneath it."
];
function openWelcome(){
 var back=el("div");style(back,{position:"fixed",inset:"0",background:"rgba(0,0,0,.78)",
  zIndex:100003,display:"flex",alignItems:"center",justifyContent:"center",padding:"16px"});
 var card=el("div");style(card,BASECSS);
 style(card,{maxWidth:"540px",width:"100%",maxHeight:"88vh",overflowY:"auto",position:"relative"});
 card.setAttribute("role","dialog");card.setAttribute("aria-label","Welcome to the calculator");
 card.appendChild(el("div",null,"<b style=\"color:"+CY+";font-size:1.25em\">Welcome to the Calculator</b>"));
 card.appendChild(el("div",null,"<span style=\"color:#8fa3bd;font-size:.9em\">The Signature Universal Paradox Immune Calculator — 9 tools, one page. Here is how to use it:</span>"));
 var ol=el("ol");ol.style.margin="10px 0 0";ol.style.paddingLeft="22px";ol.style.lineHeight="1.55";ol.style.fontSize=".95em";
 WELCOME_STEPS.forEach(function(t){var li=el("li",null,t);li.style.margin="8px 0";ol.appendChild(li)});
 card.appendChild(ol);
 var row=el("div");row.style.marginTop="8px";
 var ok=bigBtn("OK \u2014 Got it \u2713",true),full=bigBtn("Full how-to guide",false);
 ok.addEventListener("click",function(){closeW()});
 full.addEventListener("click",function(){closeW();openGuide()});
 row.appendChild(ok);row.appendChild(full);card.appendChild(row);
 function closeW(){if(back.parentNode)back.parentNode.removeChild(back);document.removeEventListener("keydown",kh);markSeen()}
 var kh=function(e){if(e.key==="Escape")closeW()};
 document.addEventListener("keydown",kh);
 back.addEventListener("click",function(e){if(e.target===back)closeW()});
 back.appendChild(card);document.body.appendChild(back);
 try{ok.focus({preventScroll:true})}catch(e){}
}

/* ---------------- the permanent guide ---------------- */
var guideBuilt=false;
function openGuide(){
 var back=el("div");style(back,{position:"fixed",inset:"0",background:"rgba(0,0,0,.72)",
  zIndex:100002,display:"flex",alignItems:"center",justifyContent:"center",padding:"16px"});
 var card=el("div");style(card,BASECSS);
 style(card,{maxWidth:"660px",width:"100%",maxHeight:"86vh",overflowY:"auto",position:"relative"});
 card.setAttribute("role","dialog");card.setAttribute("aria-label","How to use this site");
 var x=el("button",null,"\u2715");style(x,{position:"absolute",top:"8px",right:"8px",minHeight:"44px",minWidth:"44px",
  background:"none",border:"1px solid "+CY,color:"var(--txt,#dbe7f5)",borderRadius:"8px",cursor:"pointer",fontSize:"1.1em"});
 x.setAttribute("aria-label","Close guide");
 var h=el("div",null,"<b style=\"color:"+CY+";font-size:1.15em;letter-spacing:1px\">HOW TO USE THIS SITE</b><br><span style=\"color:#8fa3bd;font-size:.85em\">Signature Universal Paradox Immune Calculator \u2014 every feature, plain language.</span>");
 h.style.marginBottom="6px";card.appendChild(x);card.appendChild(h);
 GUIDE.forEach(function(g){
  var d=el("div",null,"<b style=\"color:"+CY+"\">"+g.h+"</b>");
  d.style.marginTop="12px";
  g.p.forEach(function(line){var p=el("div",null,line);p.style.fontSize=".9em";p.style.lineHeight="1.5";p.style.marginTop="4px";d.appendChild(p)});
  card.appendChild(d);
 });
 var tr=el("div");tr.style.marginTop="14px";
 var tb=bigBtn("Show the welcome guide",true);
 tb.addEventListener("click",function(){back.remove();openWelcome()});
 tr.appendChild(tb);card.appendChild(tr);
 function close(){back.remove();document.removeEventListener("keydown",kh)}
 x.addEventListener("click",close);
 back.addEventListener("click",function(e){if(e.target===back)close()});
 var kh=function(e){if(e.key==="Escape")close()};
 document.addEventListener("keydown",kh);
 back.appendChild(card);document.body.appendChild(back);
}

/* ---------------- wire up ---------------- */
function init(){
 try{
  var bar=document.getElementById("tabbar");
  if(bar&&!document.getElementById("jah-guide-btn")){
   var b=el("button",null,"? Guide");
   b.id="jah-guide-btn";b.type="button";b.className="tablink";
   b.setAttribute("aria-label","Open the welcome guide");
   b.style.marginLeft="auto";b.style.borderColor=CY;
   b.addEventListener("click",function(e){e.preventDefault();openWelcome()});
   bar.appendChild(b);
  }
 }catch(e){}
 if(!seen()){setTimeout(openWelcome,900)}
}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",init);
else init();
})();
