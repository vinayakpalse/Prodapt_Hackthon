import { useState } from "react";
import { uploadDocument, generateQuiz } from "./api";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [document, setDocument] = useState(null);

  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState("medium");
  const [generating, setGenerating] = useState(false);
  const [quizError, setQuizError] = useState("");
  const [questions, setQuestions] = useState(null);

  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  async function handleUpload(event) {
    event.preventDefault();

    if (!file) return;

    setUploading(true);
    setUploadError("");
    setDocument(null);
    setQuestions(null);
    setSubmitted(false);
    setAnswers({});

    try {
      const result = await uploadDocument(file);
      setDocument(result);
    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleGenerateQuiz() {
    if (!document) return;

    setGenerating(true);
    setQuizError("");
    setQuestions(null);
    setSubmitted(false);
    setAnswers({});

    try {
      const result = await generateQuiz(
        document.document_id,
        Number(numQuestions),
        difficulty
      );
      setQuestions(result.questions);
    } catch (error) {
      setQuizError(error.message);
    } finally {
      setGenerating(false);
    }
  }

  function selectAnswer(questionIndex, option) {
    if (submitted) return;
    setAnswers((prev) => ({ ...prev, [questionIndex]: option }));
  }

  function computeScore() {
    if (!questions) return 0;
    return questions.reduce(
      (score, q, index) =>
        answers[index] === q.correct_answer ? score + 1 : score,
      0
    );
  }

  return (
    <div className="container">
      <h1>AI Quiz Generator</h1>

      <section className="card">
        <h2>1. Upload a document</h2>
        <form onSubmit={handleUpload}>
          <input
            type="file"
            accept=".txt,.pdf,.docx,.jpg,.jpeg,.png"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <button type="submit" disabled={!file || uploading}>
            {uploading ? "Uploading..." : "Upload"}
          </button>
        </form>

        {uploadError && <p className="error">{uploadError}</p>}

        {document && (
          <div className="info">
            <p><strong>File:</strong> {document.filename}</p>
            <p><strong>Document ID:</strong> {document.document_id}</p>
            <p><strong>Pages processed:</strong> {document.pages_processed}</p>
            <p><strong>Chunks created:</strong> {document.chunks_created}</p>
          </div>
        )}
      </section>

      {document && (
        <section className="card">
          <h2>2. Generate quiz</h2>
          <div className="quiz-controls">
            <label>
              Questions:
              <input
                type="number"
                min="1"
                max="20"
                value={numQuestions}
                onChange={(e) => setNumQuestions(e.target.value)}
              />
            </label>

            <label>
              Difficulty:
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </label>

            <button onClick={handleGenerateQuiz} disabled={generating}>
              {generating ? "Generating..." : "Generate Quiz"}
            </button>
          </div>

          {quizError && <p className="error">{quizError}</p>}
        </section>
      )}

      {questions && (
        <section className="card">
          <h2>3. Take the quiz</h2>

          {questions.map((q, index) => (
            <div key={index} className="question">
              <p className="question-text">
                {index + 1}. {q.question}
              </p>

              <div className="options">
                {q.options.map((option, optIndex) => {
                  const isSelected = answers[index] === option;
                  const isCorrect = option === q.correct_answer;

                  let className = "option";
                  if (submitted && isCorrect) className += " correct";
                  if (submitted && isSelected && !isCorrect) className += " incorrect";
                  if (!submitted && isSelected) className += " selected";

                  return (
                    <label key={optIndex} className={className}>
                      <input
                        type="radio"
                        name={`question-${index}`}
                        checked={isSelected}
                        onChange={() => selectAnswer(index, option)}
                        disabled={submitted}
                      />
                      {option}
                    </label>
                  );
                })}
              </div>

              {submitted && (
                <p className="explanation">{q.explanation}</p>
              )}
            </div>
          ))}

          {!submitted ? (
            <button onClick={() => setSubmitted(true)}>Submit Quiz</button>
          ) : (
            <p className="score">
              Score: {computeScore()} / {questions.length}
            </p>
          )}
        </section>
      )}
    </div>
  );
}

export default App;
