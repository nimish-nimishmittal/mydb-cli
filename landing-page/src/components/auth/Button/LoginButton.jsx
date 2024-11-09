import React from "react";
import { useAuth0 } from "@auth0/auth0-react";

const LoginButton = () => {
  const { loginWithRedirect, isAuthenticated, user, logout } = useAuth0();

  return (
    <div>
      {isAuthenticated ? (
        <div className="flex items-center space-x-4">
          <img
            src={user.picture}
            alt={user.name}
            className="w-8 h-8 rounded-full"
          />
          
          <button
            onClick={() => logout({ returnTo: window.location.origin })}
            className="bg-red-500 text-white px-4 py-2 rounded text-sm font-medium transition duration-200 hover:bg-red-600"
          >
            Log Out
          </button>
        </div>
      ) : (
        <button
          onClick={() => loginWithRedirect()}
          className="bg-black text-white px-4 py-2 rounded text-base font-medium transition duration-200 hover:bg-gray-800"
        >
          Log In
        </button>
      )}
    </div>
  );
};

export default LoginButton;
