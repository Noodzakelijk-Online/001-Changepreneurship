import React, { useEffect, useState } from "react";

export default function QuestionView({ question }) {
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState("saved");

  useEffect(() => {
    const handle = setTimeout(() => {
      setStatus("saving");
      fetch(`/api/answers/${question.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answer })
      }).finally(() => setStatus("saved"));
    }, 600);
    return () => clearTimeout(handle);
  }, [answer, question.id]);

  const Input = question.type === "textarea" ? "textarea" : "input";

  return (
    <div>
      <label className="block mb-1">{question.prompt}</label>
      <Input
        className="w-full border rounded p-1"
        value={answer}
        onChange={(e) => setAnswer(e.target.value)}
      />
      <small className="text-xs">
        {status === "saving" ? "Saving…" : "Saved"}
      </small>
    </div>
  );
}
