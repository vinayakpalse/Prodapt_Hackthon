import { useState, useEffect, useCallback } from "react";
import { uploadDocument, generateQuiz, generateFlashcards } from "./api";
import "./App.css";

function App() {
  // Document Upload State
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [document, setDocument] = useState(null);

  // Active Mode: "quiz" | "flashcards"
  const [activeTab, setActiveTab] = useState("quiz");

  // Quiz State
  const [numQuestions, setNumQuestions] = useState(5);
  const [difficulty, setDifficulty] = useState("medium");
  const [generatingQuiz, setGeneratingQuiz] = useState(false);
  const [quizError, setQuizError] = useState("");
  const [questions, setQuestions] = useState(null);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [revealedHints, setRevealedHints] = useState({});

  // Flashcards State
  const [numCards, setNumCards] = useState(8);
  const [generatingFlashcards, setGeneratingFlashcards] = useState(false);
  const [flashcardError, setFlashcardError] = useState("");
  const [flashcards, setFlashcards] = useState(null);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [masteredCards, setMasteredCards] = useState(new Set());
  const [flashcardViewMode, setFlashcardViewMode] = useState("study"); // "study" | "grid"
  const [flippedGridCards, setFlippedGridCards] = useState({});

  async function handleUpload(event) {
    event.preventDefault();
    if (!file) return;

    setUploading(true);
    setUploadError("");
    setDocument(null);
    setQuestions(null);
    setFlashcards(null);
    setSubmitted(false);
    setAnswers({});
    setRevealedHints({});
    setMasteredCards(new Set());

    try {
      const result = await uploadDocument(file);
      setDocument(result);
    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);
    }
  }

  // Generate Quiz
  async function handleGenerateQuiz() {
    if (!document) return;

    setGeneratingQuiz(true);
    setQuizError("");
    setQuestions(null);
    setSubmitted(false);
    setAnswers({});
    setRevealedHints({});

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
      setGeneratingQuiz(false);
    }
  }

  // Generate Flashcards
  async function handleGenerateFlashcards() {
    if (!document) return;

    setGeneratingFlashcards(true);
    setFlashcardError("");
    setFlashcards(null);
    setCurrentCardIndex(0);
    setIsFlipped(false);
    setMasteredCards(new Set());
    setFlippedGridCards({});

    try {
      const result = await generateFlashcards(
        document.document_id,
        Number(numCards)
      );
      setFlashcards(result.flashcards || []);
    } catch (error) {
      setFlashcardError(error.message);
    } finally {
      setGeneratingFlashcards(false);
    }
  }

  function selectAnswer(questionIndex, option) {
    if (submitted) return;
    setAnswers((prev) => ({ ...prev, [questionIndex]: option }));
  }

  function toggleHint(questionIndex, hintIndex) {
    setRevealedHints((prev) => {
      const key = `${questionIndex}-${hintIndex}`;
      return { ...prev, [key]: !prev[key] };
    });
  }

  function computeScore() {
    if (!questions) return 0;
    return questions.reduce(
      (score, q, index) =>
        answers[index] === q.correct_answer ? score + 1 : score,
      0
    );
  }

  // Flashcard Study Navigation
  const handleNextCard = useCallback(() => {
    if (!flashcards || currentCardIndex >= flashcards.length - 1) return;
    setIsFlipped(false);
    setCurrentCardIndex((prev) => prev + 1);
  }, [flashcards, currentCardIndex]);

  const handlePrevCard = useCallback(() => {
    if (currentCardIndex <= 0) return;
    setIsFlipped(false);
    setCurrentCardIndex((prev) => prev - 1);
  }, [currentCardIndex]);

  const toggleFlip = useCallback(() => {
    setIsFlipped((prev) => !prev);
  }, []);

  const toggleMastered = useCallback((index) => {
    setMasteredCards((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  }, []);

  const shuffleDeck = () => {
    if (!flashcards) return;
    const shuffled = [...flashcards].sort(() => Math.random() - 0.5);
    setFlashcards(shuffled);
    setCurrentCardIndex(0);
    setIsFlipped(false);
    setMasteredCards(new Set());
  };

  const toggleGridCardFlip = (idx) => {
    setFlippedGridCards((prev) => ({ ...prev, [idx]: !prev[idx] }));
  };

  // Keyboard navigation for flashcards in study mode
  useEffect(() => {
    if (activeTab !== "flashcards" || !flashcards || flashcardViewMode !== "study") return;

    function handleKeyDown(e) {
      if (e.target.tagName === "INPUT" || e.target.tagName === "SELECT" || e.target.tagName === "TEXTAREA") return;
      if (e.code === "Space" || e.key === " " || e.key === "Enter") {
        e.preventDefault();
        toggleFlip();
      } else if (e.key === "ArrowRight") {
        e.preventDefault();
        handleNextCard();
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        handlePrevCard();
      } else if (e.key === "m" || e.key === "M") {
        e.preventDefault();
        toggleMastered(currentCardIndex);
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [activeTab, flashcards, flashcardViewMode, currentCardIndex, toggleFlip, handleNextCard, handlePrevCard, toggleMastered]);

  const currentCard = flashcards ? flashcards[currentCardIndex] : null;
  const isCurrentMastered = masteredCards.has(currentCardIndex);

  return (
    <div className="container">
      <header className="hero-header">
        <span className="badge-pill">AI Study Assistant</span>
        <h1>AI Knowledge & Quiz Generator</h1>
        <p className="subtitle">
          Upload any document to generate interactive multiple-choice quizzes and smart flashcards powered by RAG & Gemini AI.
        </p>
      </header>

      {/* STEP 1: Upload Document */}
      <section className="card upload-card">
        <div className="card-header">
          <span className="step-badge">Step 1</span>
          <h2>Upload Learning Material</h2>
        </div>
        <form onSubmit={handleUpload} className="upload-form">
          <div className="file-input-wrapper">
            <input
              type="file"
              id="file-upload"
              accept=".txt,.pdf,.docx,.jpg,.jpeg,.png"
              onChange={(e) => setFile(e.target.files[0])}
            />
            <label htmlFor="file-upload" className="file-label">
              {file ? file.name : "Choose PDF, DOCX, TXT or Image..."}
            </label>
          </div>
          <button type="submit" className="primary-btn" disabled={!file || uploading}>
            {uploading ? (
              <>
                <span className="spinner"></span> Processing Document...
              </>
            ) : (
              "Upload & Analyze"
            )}
          </button>
        </form>

        {uploadError && <p className="error-banner">{uploadError}</p>}

        {document && (
          <div className="doc-stats-grid">
            <div className="stat-box">
              <span className="stat-label">Document</span>
              <span className="stat-value text-truncate">{document.filename}</span>
            </div>
            <div className="stat-box">
              <span className="stat-label">Pages Extracted</span>
              <span className="stat-value">{document.pages_processed}</span>
            </div>
            <div className="stat-box">
              <span className="stat-label">Vector Chunks</span>
              <span className="stat-value">{document.chunks_created}</span>
            </div>
            <div className="stat-box">
              <span className="stat-label">FAISS Index</span>
              <span className="stat-value text-success">✓ Indexed</span>
            </div>
          </div>
        )}
      </section>

      {/* MODE TABS (Available once document is processed) */}
      {document && (
        <div className="mode-nav">
          <button
            className={`tab-btn ${activeTab === "quiz" ? "active" : ""}`}
            onClick={() => setActiveTab("quiz")}
          >
            📝 Quiz Mode {questions ? `(${questions.length})` : ""}
          </button>
          <button
            className={`tab-btn ${activeTab === "flashcards" ? "active" : ""}`}
            onClick={() => setActiveTab("flashcards")}
          >
            🎴 Flashcard Mode {flashcards ? `(${flashcards.length})` : ""}
          </button>
        </div>
      )}

      {/* ============================================================ */}
      {/* QUIZ MODE */}
      {/* ============================================================ */}
      {document && activeTab === "quiz" && (
        <>
          <section className="card config-card">
            <div className="card-header">
              <span className="step-badge">Step 2</span>
              <h2>Generate Practice Quiz</h2>
            </div>
            <div className="quiz-controls">
              <label>
                <span>Number of Questions</span>
                <input
                  type="number"
                  min="1"
                  max="20"
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(e.target.value)}
                />
              </label>

              <label>
                <span>Difficulty Level</span>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                >
                  <option value="easy">Easy (Definitions & Recall)</option>
                  <option value="medium">Medium (Concepts & Analysis)</option>
                  <option value="hard">Hard (Synthesis & Applied)</option>
                </select>
              </label>

              <button
                className="primary-btn"
                onClick={handleGenerateQuiz}
                disabled={generatingQuiz}
              >
                {generatingQuiz ? (
                  <>
                    <span className="spinner"></span> Generating with AI...
                  </>
                ) : (
                  "Generate Quiz"
                )}
              </button>
            </div>

            {quizError && <p className="error-banner">{quizError}</p>}
          </section>

          {questions && (
            <section className="card questions-card">
              <div className="card-header space-between">
                <h2>Practice Test</h2>
                <span className="badge-pill">
                  {submitted
                    ? `Final Score: ${computeScore()} / ${questions.length}`
                    : `${questions.length} Questions`}
                </span>
              </div>

              {questions.map((q, index) => {
                const isAnswered = answers[index] !== undefined;
                const isCorrect = answers[index] === q.correct_answer;

                return (
                  <div key={index} className="question-block">
                    <div className="question-header">
                      <span className="q-number">Q{index + 1}</span>
                      <p className="question-text">{q.question}</p>
                    </div>

                    {/* Progressive Hints */}
                    {q.hints && q.hints.length > 0 && (
                      <div className="hints-container">
                        {q.hints.map((hint, hIdx) => {
                          const isRevealed = revealedHints[`${index}-${hIdx}`];
                          return (
                            <div key={hIdx} className="hint-item">
                              <button
                                type="button"
                                className="hint-btn"
                                onClick={() => toggleHint(index, hIdx)}
                              >
                                {isRevealed ? `💡 Hint ${hIdx + 1}:` : `💡 Reveal Hint ${hIdx + 1}`}
                              </button>
                              {isRevealed && <span className="hint-text">{hint}</span>}
                            </div>
                          );
                        })}
                      </div>
                    )}

                    {/* Multiple-Choice Options */}
                    <div className="options-grid">
                      {q.options.map((option, optIndex) => {
                        const isSelected = answers[index] === option;
                        const isRightOption = option === q.correct_answer;

                        let optionClass = "option-pill";
                        if (submitted) {
                          if (isRightOption) optionClass += " option-correct";
                          else if (isSelected) optionClass += " option-wrong";
                        } else if (isSelected) {
                          optionClass += " option-selected";
                        }

                        return (
                          <label key={optIndex} className={optionClass}>
                            <input
                              type="radio"
                              name={`question-${index}`}
                              checked={isSelected}
                              onChange={() => selectAnswer(index, option)}
                              disabled={submitted}
                            />
                            <span className="option-letter">
                              {String.fromCharCode(65 + optIndex)}
                            </span>
                            <span className="option-label">{option}</span>
                          </label>
                        );
                      })}
                    </div>

                    {/* Detailed Explanation & Distractor Feedback */}
                    {submitted && (
                      <div className={`feedback-card ${isCorrect ? "feedback-good" : "feedback-warn"}`}>
                        <div className="feedback-badge">
                          {isCorrect ? "✓ Correct" : "✗ Incorrect"}
                        </div>
                        <p className="explanation-text">
                          <strong>Explanation:</strong> {q.explanation}
                        </p>
                        {!isCorrect && q.wrong_feedback && isAnswered && q.wrong_feedback[answers[index]] && (
                          <p className="distractor-feedback">
                            <strong>Why your answer was incorrect:</strong>{" "}
                            {q.wrong_feedback[answers[index]]}
                          </p>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}

              <div className="quiz-footer">
                {!submitted ? (
                  <button
                    className="primary-btn submit-quiz-btn"
                    onClick={() => setSubmitted(true)}
                    disabled={Object.keys(answers).length === 0}
                  >
                    Submit Quiz & Review Answers
                  </button>
                ) : (
                  <div className="score-summary">
                    <div className="score-badge">
                      Score: {computeScore()} / {questions.length} (
                      {Math.round((computeScore() / questions.length) * 100)}%)
                    </div>
                    <button
                      className="secondary-btn"
                      onClick={() => {
                        setSubmitted(false);
                        setAnswers({});
                        setRevealedHints({});
                      }}
                    >
                      Retake Quiz
                    </button>
                  </div>
                )}
              </div>
            </section>
          )}
        </>
      )}

      {/* ============================================================ */}
      {/* FLASHCARD MODE */}
      {/* ============================================================ */}
      {document && activeTab === "flashcards" && (
        <>
          <section className="card config-card">
            <div className="card-header">
              <span className="step-badge">Step 2</span>
              <h2>Generate Smart Flashcards</h2>
            </div>
            <div className="quiz-controls">
              <label>
                <span>Number of Flashcards</span>
                <input
                  type="number"
                  min="1"
                  max="30"
                  value={numCards}
                  onChange={(e) => setNumCards(e.target.value)}
                />
              </label>

              <div className="quick-presets">
                <span className="preset-label">Quick select:</span>
                {[5, 10, 15, 20].map((count) => (
                  <button
                    key={count}
                    type="button"
                    className={`preset-btn ${numCards === count ? "active" : ""}`}
                    onClick={() => setNumCards(count)}
                  >
                    {count}
                  </button>
                ))}
              </div>

              <button
                className="primary-btn"
                onClick={handleGenerateFlashcards}
                disabled={generatingFlashcards}
              >
                {generatingFlashcards ? (
                  <>
                    <span className="spinner"></span> Creating Cards...
                  </>
                ) : (
                  "Generate Flashcards"
                )}
              </button>
            </div>

            {flashcardError && <p className="error-banner">{flashcardError}</p>}
          </section>

          {flashcards && flashcards.length > 0 && (
            <section className="card flashcards-section">
              {/* Flashcard Header Bar */}
              <div className="flashcards-top-bar">
                <div className="deck-info">
                  <h2>Flashcards Deck</h2>
                  <div className="mastery-counter">
                    <span className="mastery-pill">
                      ★ {masteredCards.size} of {flashcards.length} Mastered
                    </span>
                  </div>
                </div>

                <div className="view-switch-group">
                  <button
                    className={`view-btn ${flashcardViewMode === "study" ? "active" : ""}`}
                    onClick={() => setFlashcardViewMode("study")}
                  >
                    Interactive Flip
                  </button>
                  <button
                    className={`view-btn ${flashcardViewMode === "grid" ? "active" : ""}`}
                    onClick={() => setFlashcardViewMode("grid")}
                  >
                    Grid View
                  </button>
                  <button className="icon-btn" title="Shuffle Deck" onClick={shuffleDeck}>
                    🔀 Shuffle
                  </button>
                </div>
              </div>

              {/* STUDY MODE: 3D FLIP CARD */}
              {flashcardViewMode === "study" && currentCard && (
                <div className="study-container">
                  {/* Progress bar */}
                  <div className="progress-bar-wrapper">
                    <div
                      className="progress-bar-fill"
                      style={{
                        width: `${((currentCardIndex + 1) / flashcards.length) * 100}%`,
                      }}
                    ></div>
                  </div>

                  <div className="study-status-line">
                    <span>
                      Card <strong>{currentCardIndex + 1}</strong> of{" "}
                      <strong>{flashcards.length}</strong>
                    </span>
                    <span className="keyboard-hint">
                      Shortcut: <kbd>Space</kbd> to flip • <kbd>←</kbd> <kbd>→</kbd> navigate • <kbd>M</kbd> master
                    </span>
                  </div>

                  {/* 3D Flip Card */}
                  <div className="flip-scene" onClick={toggleFlip}>
                    <div className={`flip-card-inner ${isFlipped ? "flipped" : ""}`}>
                      {/* FRONT */}
                      <div className="flip-card-face flip-card-front">
                        <div className="card-top-row">
                          <span className="topic-badge">{currentCard.topic || "Concept"}</span>
                          {isCurrentMastered && (
                            <span className="mastered-badge">✓ Mastered</span>
                          )}
                        </div>
                        <div className="card-body-content">
                          <p className="card-label">QUESTION / PROMPT</p>
                          <h3 className="card-prompt-text">{currentCard.front}</h3>
                        </div>
                        <div className="card-bottom-hint">
                          <span>🔄 Click or press Space to flip answer</span>
                        </div>
                      </div>

                      {/* BACK */}
                      <div className="flip-card-face flip-card-back">
                        <div className="card-top-row">
                          <span className="topic-badge">{currentCard.topic || "Answer"}</span>
                          <span className="back-indicator">Answer</span>
                        </div>
                        <div className="card-body-content">
                          <p className="card-label">EXPLANATION & DETAILS</p>
                          <p className="card-answer-text">{currentCard.back}</p>
                        </div>
                        <div className="card-bottom-hint">
                          <span>🔄 Click or press Space to flip back</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Navigation & Mastery Controls */}
                  <div className="flashcard-actions">
                    <button
                      className="secondary-btn nav-btn"
                      onClick={handlePrevCard}
                      disabled={currentCardIndex === 0}
                    >
                      ← Previous
                    </button>

                    <button className="primary-btn flip-btn" onClick={toggleFlip}>
                      🔄 Flip Card
                    </button>

                    <button
                      className={`master-btn ${isCurrentMastered ? "is-mastered" : ""}`}
                      onClick={() => toggleMastered(currentCardIndex)}
                    >
                      {isCurrentMastered ? "★ Mastered" : "☆ Mark as Mastered"}
                    </button>

                    <button
                      className="secondary-btn nav-btn"
                      onClick={handleNextCard}
                      disabled={currentCardIndex === flashcards.length - 1}
                    >
                      Next →
                    </button>
                  </div>
                </div>
              )}

              {/* GRID MODE: ALL CARDS */}
              {flashcardViewMode === "grid" && (
                <div className="flashcards-grid">
                  {flashcards.map((card, idx) => {
                    const isCardFlipped = flippedGridCards[idx];
                    const isCardMastered = masteredCards.has(idx);

                    return (
                      <div
                        key={idx}
                        className={`grid-flip-card ${isCardFlipped ? "flipped" : ""}`}
                        onClick={() => toggleGridCardFlip(idx)}
                      >
                        <div className="grid-flip-inner">
                          {/* Front */}
                          <div className="grid-face grid-face-front">
                            <div className="grid-top">
                              <span className="topic-badge">{card.topic || "Concept"}</span>
                              <span className="card-index-tag">#{idx + 1}</span>
                            </div>
                            <h4 className="grid-card-title">{card.front}</h4>
                            <div className="grid-footer">
                              <span className="flip-tag">Click to flip</span>
                              <button
                                type="button"
                                className={`star-btn ${isCardMastered ? "starred" : ""}`}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  toggleMastered(idx);
                                }}
                              >
                                {isCardMastered ? "★" : "☆"}
                              </button>
                            </div>
                          </div>

                          {/* Back */}
                          <div className="grid-face grid-face-back">
                            <div className="grid-top">
                              <span className="topic-badge">{card.topic || "Answer"}</span>
                              <span className="answer-tag">Answer</span>
                            </div>
                            <p className="grid-card-answer">{card.back}</p>
                            <div className="grid-footer">
                              <span className="flip-tag">Click to flip back</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </section>
          )}
        </>
      )}
    </div>
  );
}

export default App;
