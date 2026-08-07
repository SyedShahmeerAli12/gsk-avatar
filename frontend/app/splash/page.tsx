"use client";
import { useRouter } from "next/navigation";

export default function SplashPage() {
  const router = useRouter();

  return (
    <div
      className="relative w-full overflow-hidden"
      style={{
        minHeight: "100dvh",
        background:
          "radial-gradient(70% 55% at -5% 108%, rgba(250,140,80,.30) 0%, rgba(252,190,155,.14) 45%, rgba(255,255,255,0) 78%), linear-gradient(160deg,#fefdfc 0%,#fdfbfa 55%,#fdfaf8 100%)",
        backgroundAttachment: "fixed",
        fontFamily: "'Poppins', system-ui, sans-serif",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800;900&display=swap');
        @media (max-width: 640px) {
          .splash-left { padding-left: 6vw !important; padding-right: 6vw !important; }
          .splash-hero-row { flex-direction: column !important; align-items: flex-start !important; gap: 16px !important; }
          .splash-divider { display: none !important; }
          .splash-subtitle { margin-left: 0 !important; margin-top: 20px !important; }
          .splash-start-btn { margin-left: 0 !important; width: 100% !important; max-width: 100% !important; }
        }
      `}</style>

      {/* Right-side circular artwork — desktop only */}
      <div className="absolute inset-y-0 right-0 hidden md:block pointer-events-none select-none">
        <div className="absolute rounded-full" style={{ width:"128vh", height:"128vh", top:"50%", right:"-34vh", transform:"translateY(-50%)", background:"#fdeee6" }} />
        <div className="absolute rounded-full" style={{ width:"118vh", height:"118vh", top:"50%", right:"-32vh", transform:"translateY(-50%)", background:"linear-gradient(150deg,#0a1030 0%,#1a2555 55%,#2b3a7a 100%)" }} />
        <div className="absolute rounded-full overflow-hidden" style={{ width:"104vh", height:"104vh", top:"50%", right:"-30vh", transform:"translateY(-50%)", background:"radial-gradient(circle at 38% 42%, #1e2d6b 0%, #0f1a45 45%, #080e28 100%)" }}>
          <PatientArt />
        </div>
        {/* Feature badges */}
        <div className="absolute flex flex-col gap-[3.2vh]" style={{ right:"13vh", top:"52%" }}>
          <Badge label="Realistic" />
          <Badge label="Clinical" />
          <Badge label="Training" />
        </div>
      </div>

      {/* Bottom-left wave lines */}
      <svg viewBox="0 0 900 220" preserveAspectRatio="none" className="absolute bottom-0 left-0 w-[70%] h-[26vh] pointer-events-none" fill="none">
        {Array.from({ length: 22 }).map((_, i) => (
          <path key={i}
            d={`M -40 ${120 + i * 4.5} C 180 ${60 + i * 4.5}, 300 ${190 + i * 4.5}, 520 ${132 + i * 4.5} S 800 ${58 + i * 4.5}, 940 ${104 + i * 4.5}`}
            stroke="#f3b391" strokeWidth="0.7" opacity={0.16 - i * 0.004}
          />
        ))}
      </svg>

      {/* Left content */}
      <div className="splash-left relative z-10 flex flex-col w-full md:w-[58%] lg:w-[52%] px-[6vw] md:px-[5vw] py-[5vh]" style={{ minHeight:"100dvh" }}>

        {/* GSK Logo */}
        <div className="flex flex-col leading-none">
          <div className="flex items-center gap-3">
            <span className="font-black" style={{ fontSize:"clamp(28px,3.4vw,46px)", letterSpacing:"0.14em", color:"#0a1030" }}>GSK</span>
            <span className="font-bold px-3 py-1 rounded-md text-white" style={{ fontSize:"clamp(11px,1vw,15px)", letterSpacing:"0.1em", background:"linear-gradient(118deg,#fe7d2e,#f53e2a)" }}>AUGMENTIN</span>
          </div>
          <span className="font-semibold" style={{ fontSize:"clamp(10px,1vw,14px)", letterSpacing:"0.42em", marginTop:"clamp(2px,0.4vw,6px)", color:"#2b3550" }}>AI PATIENT SIMULATOR</span>
        </div>

        {/* Hero block */}
        <div className="flex flex-col my-auto" style={{ paddingBottom:"6vh" }}>
          <div className="splash-hero-row flex items-center" style={{ gap:"clamp(16px,2vw,30px)" }}>
            <PatientIcon />
            <div className="splash-divider w-px self-stretch bg-[#f3b391]" style={{ minHeight:"clamp(90px,11vw,150px)" }} />
            <div className="flex flex-col">
              <h1 className="font-extrabold leading-[1.02]" style={{ fontSize:"clamp(30px,4.2vw,56px)", letterSpacing:"-0.01em", color:"#0a1030" }}>
                AI PATIENT
              </h1>
              <h1 className="font-extrabold leading-[1.02]" style={{ fontSize:"clamp(30px,4.2vw,56px)", letterSpacing:"-0.01em", background:"linear-gradient(118deg,#fe7d2e,#f53e2a)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent" }}>
                SIMULATION
              </h1>
              <p className="font-medium" style={{ fontSize:"clamp(14px,1.7vw,22px)", letterSpacing:"0.13em", marginTop:"clamp(6px,0.9vw,14px)", color:"#2b3550" }}>
                DOCTOR TRAINING
              </p>
              <div className="flex" style={{ marginTop:"clamp(12px,1.6vw,22px)" }}>
                <div className="h-[3px]" style={{ width:"clamp(34px,3.4vw,50px)", background:"#0a1030" }} />
                <div className="h-[3px]" style={{ width:"clamp(14px,1.4vw,20px)", background:"#fe7d2e" }} />
              </div>
            </div>
          </div>

          <div className="splash-subtitle text-[#6b7089]" style={{ fontSize:"clamp(14px,1.3vw,18px)", lineHeight:1.65, marginTop:"clamp(24px,3.6vw,48px)", marginLeft:"clamp(0px,10vw,140px)" }}>
            <p>Consult. Diagnose. Learn.</p>
            <p>Practice real patient interactions before the clinic.</p>
          </div>

          <button
            onClick={() => router.push("/")}
            className="splash-start-btn text-white font-bold transition-all active:scale-[0.98]"
            style={{
              marginTop:"clamp(26px,3.6vw,50px)",
              marginLeft:"clamp(0px,10vw,140px)",
              width:"clamp(240px,26vw,382px)",
              paddingTop:"clamp(16px,1.75vw,24px)",
              paddingBottom:"clamp(16px,1.75vw,24px)",
              borderRadius:"clamp(10px,0.95vw,14px)",
              fontSize:"clamp(17px,1.8vw,24px)",
              letterSpacing:"0.06em",
              background:"linear-gradient(118deg,#fe7d2e 0%,#fa5a22 48%,#f53e2a 100%)",
              boxShadow:"0 16px 36px rgba(245,80,35,.30)",
            }}
          >
            START SESSION
          </button>
        </div>
      </div>
    </div>
  );
}

function PatientIcon() {
  return (
    <svg viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg"
      style={{ width:"clamp(64px,8.4vw,118px)", height:"clamp(64px,8.4vw,118px)", flexShrink:0 }}>
      <circle cx="60" cy="38" r="22" stroke="#fe7d2e" strokeWidth="3.2" fill="none" />
      <path d="M28 100 C28 78 92 78 92 100" stroke="#0a1030" strokeWidth="3.2" strokeLinecap="round" fill="none" />
      <circle cx="60" cy="38" r="10" fill="#0a1030" opacity="0.12" />
      <path d="M50 38 Q60 30 70 38" stroke="#fe7d2e" strokeWidth="2.4" strokeLinecap="round" fill="none" />
      <circle cx="54" cy="40" r="2.5" fill="#0a1030" />
      <circle cx="66" cy="40" r="2.5" fill="#0a1030" />
      <path d="M54 46 Q60 52 66 46" stroke="#0a1030" strokeWidth="2" strokeLinecap="round" fill="none" />
    </svg>
  );
}

function PatientArt() {
  return (
    <svg viewBox="0 0 660 760" fill="none" className="absolute inset-0 w-full h-full" preserveAspectRatio="xMidYMid meet">
      <defs>
        <radialGradient id="pg" cx="50%" cy="46%">
          <stop offset="0%" stopColor="#fe7d2e" stopOpacity="0.22" />
          <stop offset="55%" stopColor="#fa5a22" stopOpacity="0.08" />
          <stop offset="100%" stopColor="#f53e2a" stopOpacity="0" />
        </radialGradient>
      </defs>
      <ellipse cx="325" cy="350" rx="300" ry="330" fill="url(#pg)" />
      {/* Head */}
      <ellipse cx="330" cy="220" rx="90" ry="110" fill="#c8a882" opacity="0.9" />
      {/* Body */}
      <path d="M220 640 L240 420 Q330 380 420 420 L440 640 Z" fill="#3a5a8a" opacity="0.7" />
      {/* Collar / shirt detail */}
      <path d="M290 420 L330 460 L370 420" stroke="#fff" strokeWidth="2" opacity="0.5" fill="none" />
      {/* Face features */}
      <ellipse cx="310" cy="210" rx="8" ry="9" fill="#6b3a2a" opacity="0.7" />
      <ellipse cx="350" cy="210" rx="8" ry="9" fill="#6b3a2a" opacity="0.7" />
      <path d="M312 238 Q330 250 348 238" stroke="#6b3a2a" strokeWidth="2.5" strokeLinecap="round" fill="none" opacity="0.7" />
      {/* Hair */}
      <ellipse cx="330" cy="130" rx="92" ry="55" fill="#2b1a10" opacity="0.85" />
      {/* Dupatta hint */}
      <path d="M240 340 Q330 310 420 340 L440 420 Q330 390 220 420 Z" fill="#1e3a6b" opacity="0.5" />
      {/* floating particles */}
      {[[92,236,3.2],[572,292,2.6],[120,470,2.2],[560,470,3.4],[212,76,2.4],[452,62,2.8]].map(([x,y,r],i)=>(
        <circle key={i} cx={x} cy={y} r={r} fill="#fe7d2e" opacity="0.4" />
      ))}
    </svg>
  );
}

function Badge({ label }: { label: string }) {
  return (
    <div className="flex items-center justify-center" style={{ width:"clamp(46px,5.4vh,74px)", height:"clamp(52px,6.1vh,84px)", clipPath:"polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%)", background:"rgba(254,125,46,0.16)", boxShadow:"inset 0 0 0 1.2px rgba(254,125,46,0.45)" }}>
      <span style={{ fontSize:"clamp(7px,0.9vh,11px)", color:"#fee0cc", fontWeight:700, letterSpacing:"0.04em", textAlign:"center" }}>{label}</span>
    </div>
  );
}
