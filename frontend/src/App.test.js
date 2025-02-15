import { render, screen } from '@testing-library/react';
import Chatbot from './components/chatbot/Chatbot_websocket';

test('renders initial chatbot message', () => {
  render(<Chatbot />);
  const messageElement = screen.getByText(/Whispers of wisdom await... Ask your question!/i);  // This is the message shown on initial render
  expect(messageElement).toBeInTheDocument();  // Verify that it's in the document
});


// this is a test script that will run during CI to test the front-end
// we are basically checking if the text" Whispers of wisdom await... Ask your question"
// is the first text on chatbot