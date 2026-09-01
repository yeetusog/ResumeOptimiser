export default function ATSGauge({ score }) {
  const value = Math.max(0, Math.min(100, Number(score) || 0));
  const radius = 58;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (value / 100) * circumference;
  const tone = value >= 75 ? "#0f9f85" : value >= 45 ? "#b88214" : "#e05a47";

  return (
    <div className="flex items-center gap-5 rounded border border-line bg-white p-4 shadow-sm">
      <svg width="140" height="140" viewBox="0 0 140 140" role="img" aria-label={`ATS score ${value}`}>
        <circle cx="70" cy="70" r={radius} fill="none" stroke="#e8ecf3" strokeWidth="12" />
        <circle
          cx="70"
          cy="70"
          r={radius}
          fill="none"
          stroke={tone}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 70 70)"
          className="transition-all duration-700 ease-out"
        />
        <text x="70" y="66" textAnchor="middle" className="fill-ink text-3xl font-bold">
          {Math.round(value)}
        </text>
        <text x="70" y="88" textAnchor="middle" className="fill-slate-500 text-xs font-semibold">
          ATS
        </text>
      </svg>
      <div className="min-w-0">
        <p className="text-sm font-semibold text-ink">Match Score</p>
        <p className="mt-1 text-sm text-slate-600">Updates after scoring or optimization.</p>
      </div>
    </div>
  );
}
