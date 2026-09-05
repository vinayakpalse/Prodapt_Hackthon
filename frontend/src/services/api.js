import { mockTopics, mockFlashcards, mockQuizzes, mockQuestions, mockProgress, mockActivity } from '../data/mockData';

// Simulate network delay
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export const uploadDocument = async (file) => {
  await delay(3000); // Simulate processing time
  return { success: true, message: 'Document processed successfully', topics: mockTopics };
};

export const getTopics = async () => {
  await delay(500);
  return mockTopics;
};

export const getQuizzes = async () => {
  await delay(500);
  return mockQuizzes;
};

export const getFlashcardsByTopic = async (topicId) => {
  await delay(800);
  return mockFlashcards; // Returning the same mock for now
};

export const getQuizQuestions = async (quizId) => {
  await delay(800);
  return mockQuestions;
};

export const getProgress = async () => {
  await delay(500);
  return mockProgress;
};

export const getActivity = async () => {
  await delay(500);
  return mockActivity;
};
