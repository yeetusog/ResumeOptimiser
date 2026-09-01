export default function JDInput({ jdText, setJdText, targetTitle, setTargetTitle, proficiencies, setProficiencies }) {
  return (
    <section className="space-y-3">
      <h2 className="text-base font-semibold text-ink">Target Role</h2>
      <input
        value={targetTitle}
        onChange={(event) => setTargetTitle(event.target.value)}
        className="focus-ring w-full rounded border border-line bg-white px-3 py-2 text-sm shadow-sm"
        placeholder="Senior Backend Engineer"
      />
      <textarea
        value={proficiencies}
        onChange={(event) => setProficiencies(event.target.value)}
        className="focus-ring h-20 w-full resize-none rounded border border-line bg-white p-3 text-sm shadow-sm"
        placeholder="Your strongest proficiencies, separated by commas"
      />
      <textarea
        value={jdText}
        onChange={(event) => setJdText(event.target.value)}
        className="focus-ring h-56 w-full resize-none rounded border border-line bg-white p-3 text-sm shadow-sm"
        placeholder="Paste the job description."
      />
    </section>
  );
}
