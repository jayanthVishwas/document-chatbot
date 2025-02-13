import React, { useState, useEffect } from 'react';
import '../../App.css'; // Make sure to import your CSS file

const Typewriter = ({ text }) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [textColor, setTextColor] = useState('black'); // Default text color

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeoutId = setTimeout(() => {
        setDisplayedText((prev) => prev + text[currentIndex]);
        setCurrentIndex((prev) => prev + 1);
      }, 120); // Adjust the timing for character appearance speed

      return () => clearTimeout(timeoutId);
    } else {
      // Change text color to white after 10 seconds
      const hideTimeoutId = setTimeout(() => {
        setTextColor('black');
      }, 10000); // 10 seconds

      return () => clearTimeout(hideTimeoutId);
    }
  }, [currentIndex, text]);

  return (
    <span className="typewriter">
      <span className="typewriter-text" style={{ color: textColor }}>
        {displayedText}
      </span>
    </span>
  );
};

export default Typewriter;





