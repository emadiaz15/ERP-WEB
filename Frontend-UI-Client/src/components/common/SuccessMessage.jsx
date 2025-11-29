// src/components/common/SuccessMessage.jsx
import React, { useEffect } from 'react';

// Ligero toast no bloqueante. Se auto-cierra y NO hace reload.
const SuccessMessage = ({ message, onClose = () => { }, autoCloseMs = 2500 }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, autoCloseMs);
    return () => clearTimeout(timer);
  }, [onClose, autoCloseMs]);

  return (
    <div className="bg-success-500 text-white px-4 py-2 rounded-lg shadow-md">
      {message}
    </div>
  );
};

export default SuccessMessage;
