import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/authContext';
import { doSignOut } from '../../firebase/auth';

const Header = () => {
  const navigate = useNavigate();
  const { userLoggedIn } = useAuth();

  return (
    <nav className='flex justify-center items-center w-full z-20 fixed top-0 left-0 h-12  bg-whte-200 px-4'>
      {userLoggedIn ? (
        <button
          onClick={() => {
            doSignOut().then(() => {
              navigate('/login');
            });
          }}
          className='w-44 px-4 py-2 text-sm text-white bg-blue-600 rounded hover:bg-blue-700 transition duration-300 absolute right-4'
        >
          Logout
        </button>
      ) : (
        <div className='flex gap-x-4'>
          <button
            onClick={() => navigate('/login')}
            className='w-44 px-4 py-2 text-sm text-white bg-blue-600 rounded hover:bg-blue-700 transition duration-300'
          >
            Login
          </button>
          <button
            onClick={() => navigate('/register')}
            className='w-44 px-4 py-2 text-sm text-white bg-green-600 rounded hover:bg-green-700 transition duration-300'
          >
            Sign Up
          </button>
        </div>
      )}
    </nav>
  );
};

export default Header;


