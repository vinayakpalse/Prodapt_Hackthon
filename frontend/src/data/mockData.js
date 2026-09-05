export const mockTopics = [
  { id: '1', name: 'Processes', flashcardCount: 24 },
  { id: '2', name: 'CPU Scheduling', flashcardCount: 18 },
  { id: '3', name: 'Deadlocks', flashcardCount: 15 },
  { id: '4', name: 'Memory Management', flashcardCount: 21 },
  { id: '5', name: 'Threads', flashcardCount: 12 },
];

export const mockFlashcards = [
  { id: '1', topicId: '3', question: 'What is Deadlock?', answer: 'A deadlock occurs when two or more processes are unable to proceed because each is waiting for one of the others to do something.' },
  { id: '2', topicId: '3', question: 'What is Mutual Exclusion?', answer: 'At least one resource must be held in a non-shareable mode.' },
  { id: '3', topicId: '3', question: 'What is Hold and Wait?', answer: 'A process must be holding at least one resource and waiting to acquire additional resources held by other processes.' },
  { id: '4', topicId: '3', question: 'What is No Preemption?', answer: 'Resources cannot be preempted; a resource can be released only voluntarily by the process holding it.' },
];

export const mockQuizzes = [
  { id: '1', title: 'Operating Systems Quiz', questionCount: 20, difficulty: 'Medium', estimatedTime: 10 },
  { id: '2', title: 'Deadlocks Practice', questionCount: 10, difficulty: 'Hard', estimatedTime: 5 },
];

export const mockQuestions = [
  {
    id: '1',
    quizId: '2',
    question: 'Which of the following is a necessary condition for deadlock?',
    options: ['Mutual Exclusion', 'Context Switching', 'Multitasking', 'Virtual Memory'],
    correctAnswer: 'Mutual Exclusion',
    explanation: 'Mutual exclusion is one of the four necessary conditions for deadlock, meaning at least one resource must be non-shareable.',
    topic: 'Deadlocks'
  },
  {
    id: '2',
    quizId: '2',
    question: 'What happens in a circular wait condition?',
    options: [
      'A set of processes are waiting for each other in a circular form',
      'A process waits for itself',
      'The CPU waits for I/O in a loop',
      'None of the above'
    ],
    correctAnswer: 'A set of processes are waiting for each other in a circular form',
    explanation: 'Circular wait occurs when a set of waiting processes {P0, P1, ..., Pn} exist such that P0 is waiting for a resource held by P1, P1 is waiting for P2, and so on.',
    topic: 'Deadlocks'
  },
  {
    id: '3',
    quizId: '2',
    question: 'Can deadlock occur if there is only one instance of every resource type?',
    options: ['Yes, if a cycle exists in the resource allocation graph', 'No, cycles do not matter', 'Only in distributed systems', 'It depends on the CPU'],
    correctAnswer: 'Yes, if a cycle exists in the resource allocation graph',
    explanation: 'If each resource type has exactly one instance, then a cycle in the resource allocation graph is both a necessary and sufficient condition for a deadlock.',
    topic: 'Deadlocks'
  }
];

export const mockProgress = {
  quizzesTaken: 12,
  questionsAnswered: 126,
  averageScore: 82,
  flashcardsReviewed: 84
};

export const mockActivity = [
  { id: 1, type: 'quiz', text: 'Completed Deadlocks Quiz', score: 80, date: '2 hours ago' },
  { id: 2, type: 'flashcard', text: 'Reviewed CPU Scheduling flashcards', count: 12, date: '5 hours ago' },
  { id: 3, type: 'quiz', text: 'Completed Operating Systems Quiz', score: 90, date: '1 day ago' }
];
